import ipyvuetify as v

from .pylbmwidget import out

import enum
import sympy as sp
from traitlets import Unicode, Float, List, Bool

from schema.utils import SchemeVelocity, RelaxationParameterFinal
from ..utils import required_fields

class DesignForm(v.Form):
    def __init__(self, test_case_widget, lb_scheme_widget):
        self.test_case_widget, self.lb_scheme_widget = test_case_widget, lb_scheme_widget
        self.params, self.relax_params = None, None

        self.select_param = v.Select(label='Parameters', v_model=None, items=[], multiple=False, required=True)
        self.select_relax = v.Select(label='Relaxation parameters', v_model=[], items=[], multiple=True, required=True, class_='d-none')
        self.srt_relax = v.Switch(label='Single relaxation time', v_model=True, class_='d-none')
        self.min = v.TextField(label='Enter the minimum', v_model=None, required=True, class_='d-none')
        self.max = v.TextField(label='Enter the maximum', v_model=None, required=True, class_='d-none')

        self.update_select_fields(None)

        test_case_widget.select_case.observe(self.update_select_fields, 'v_model')
        lb_scheme_widget.select_case.observe(self.update_select_fields, 'v_model')
        self.select_param.observe(self.select_param_changed, 'v_model')
        self.select_relax.observe(self.select_relax_rules, 'v_model')
        self.select_relax.observe(self.select_relax_all, 'v_model')
        self.min.observe(self.minmax_rules, 'v_model')
        self.max.observe(self.minmax_rules, 'v_model')

        super().__init__(v_model='valid', children=[self.select_param, self.select_relax, self.srt_relax, self.min, self.max])

    def update_select_fields(self, change):
        fields = required_fields(self.test_case_widget.get_case())
        fields.update(required_fields(self.lb_scheme_widget.get_case()))

        params = {'relaxation parameters': None}
        params.update({f: v['value'] for f, v in fields.items() if v['type'] != 'relaxation parameter'})
        relax_params = {f: v['value'] for f, v in fields.items() if v['type'] == 'relaxation parameter'}

        self.params = {k: params[k] for k in sorted(params)}
        self.relax_params = {k: relax_params[k] for k in sorted(relax_params)}

        self.select_param.items = list(self.params.keys())
        self.select_relax.items = ['all'] + list(self.relax_params.keys())

    def select_param_changed(self, change):
        with out:
            if self.select_param.v_model:
                if self.select_param.v_model == 'relaxation parameters':
                    self.min.v_model = 1
                    self.max.v_model = 1
                    self.select_relax.class_ = ''
                    self.srt_relax.class_ = ''
                else:
                    value = self.params[self.select_param.v_model]
                    self.min.v_model = value
                    self.max.v_model = value
                    self.select_relax.class_ = 'd-none'
                    self.srt_relax.class_ = 'd-none'
                    self.select_relax.v_model = []
                self.min.class_ = ''
                self.max.class_ = ''
                self.min.notify_change({'name': 'v_model', 'type': 'change'})
                self.max.notify_change({'name': 'v_model', 'type': 'change'})

    def select_relax_all(self, change):
        if 'all' in self.select_relax.v_model:
            self.select_relax.v_model = list(self.relax_params.keys())

    def select_relax_rules(self, change):
        with out:
            if self.select_param.v_model == 'relaxation parameters':
                if self.select_relax.v_model == []:
                    self.select_relax.rules = ['You must select at least one relaxation parameter']
                    self.select_relax.error = True
                    return False
                else:
                    self.select_relax.rules = []
                    self.select_relax.error = False
                    return True
            return True

    def minmax_rules(self, change):
        output = True
        if self.min.v_model and self.max.v_model:
            min, max = float(self.min.v_model), float(self.max.v_model)
            if min == max:
                self.min.rules = ['Min must be different from Max']
                self.min.error = True
                self.max.rules = ['Max must be different from Min']
                self.max.error = True
                output &= False
            elif min > max:
                self.min.rules = ['Min must be lower than Max']
                self.min.error = True
                self.max.rules = ['Max must be greater than Min']
                self.max.error = True
                output &= False
            elif self.select_param.v_model == 'relaxation parameters':
                if min < 0 or min > 2:
                    self.min.rules = ['Min must be in [0, 2]']
                    self.min.error = True
                    output &= False
                else:
                    self.min.rules = []
                    self.min.error = False
                    output &= True

                if max < 0 or max > 2:
                    self.max.rules = ['Max must be in [0, 2]']
                    self.max.error = True
                    output &= False
                else:
                    self.max.rules = []
                    self.max.error = False
                    output &= True
            else:
                self.min.rules = []
                self.min.error = False
                self.max.rules = []
                self.max.error = False
        return output

    def check_rules(self):
        self.v_model = True
        self.v_model &= self.select_relax_rules(None)
        self.v_model &= self.minmax_rules(None)

    def reset_form(self):
        self.select_param.v_model = None
        self.select_param.rules = []
        self.select_param.error = False

        self.select_relax.v_model = []
        self.select_relax.rules = []
        self.select_relax.error = False
        self.select_relax.class_ = 'd-none'
        self.srt_relax = True
        self.srt_relax.class_ = 'd-none'

        self.min.v_model = None
        self.min.rules = []
        self.min.error = False
        self.min.class_ = 'd-none'

        self.max.v_model = None
        self.max.rules = []
        self.max.error = False
        self.max.class_ = 'd-none'

        self.v_model = False

    def __str__(self):
        if self.select_param.v_model == 'relaxation parameters':
            return ', '.join(self.select_relax.v_model) + f' (srt: {self.srt_relax.v_model}, min: {self.min.v_model}, max: {self.max.v_model})'
        else:
            return f'{self.select_param.v_model} (min: {self.min.v_model}, max: {self.max.v_model})'

class DesignItem(v.ListItem):
    def __init__(self, content, test_case_widget, lb_scheme_widget, form, **kwargs):
        self.form = DesignForm(test_case_widget, lb_scheme_widget)

        self.param = form.select_param.v_model
        self.relax = form.select_relax.v_model
        self.srt = form.srt_relax.v_model
        self.min = float(form.min.v_model)
        self.max = float(form.max.v_model)

        update_btn = v.Btn(children=['update'], color='success')
        close_btn = v.Btn(children=['close'], color='error')

        self.update_dialog = v.Dialog(
            width='500',
            v_model=False,
            children=[
                v.Card(children=[
                    v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                        "Update field range configuration"
                    ]),
                    v.CardText(children=[self.form]),
                    v.CardActions(children=[v.Spacer(), update_btn, close_btn])
            ]),
        ])

        update_btn.on_event('click', self.update_click)
        close_btn.on_event('click', self.close_click)

        self.content = v.CardText(children=[content])

        self.btn = v.Btn(children=[v.Icon(children=['mdi-close'])],
                        fab=True,
                        color='error',
                        dark=True,
                        x_small=True,
        )

        super().__init__(children=[
            v.ListItemAction(children=[self.btn]),
            v.ListItemContent(
                children=[
                    v.Card(children=[self.content],
                        flat=True,
                        color='transparent',
                        light=True,
                    ),
                self.update_dialog
                ]),
            ], **kwargs)

    def close_click(self, widget, event, data):
        self.update_dialog.v_model = False

    def update_click(self, widget, event, data):
        self.form.check_rules()

        if self.form.v_model:
            self.param = self.form.select_param.v_model
            self.relax = self.form.select_relax.v_model
            self.srt = self.form.srt_relax.v_model
            self.min = float(self.form.min.v_model)
            self.max = float(self.form.max.v_model)
            self.content.children = [f'{self.form}']
            self.update_dialog.v_model = False

    def update_chip(self, widget, event, data):
        self.form.reset_form()
        self.form.select_param.v_model = self.param
        self.form.select_relax.v_model = self.relax
        self.form.srt_relax.v_model = self.srt
        self.form.min.v_model =  self.min
        self.form.max.v_model =  self.max
        self.update_dialog.v_model = True

class Design_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget

        form = DesignForm(test_case_widget, lb_scheme_widget)

        create_add = v.Btn(children=['add'], color='success')
        create_close = v.Btn(children=['close'], color='error')

        create_dialog = v.Dialog(
            width='500',
            v_model=False,
            children=[
                v.Card(children=[
                    v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                        "New field range configuration"
                    ]),
                    v.CardText(children=[form]),
                    v.CardActions(children=[v.Spacer(), create_add, create_close])
            ]),
        ])

        self.design_list = v.List(children=[])
        add_button = v.Btn(children=[v.Icon(children=['mdi-plus']), create_dialog],
                           fab=True,
                           color='primary',
                           small=True,
                           dark=True,
        )

        def close_click(widget, event, data):
            create_dialog.v_model = False

        def add_click(widget, event, data):
            form.check_rules()

            if form.v_model:
                new_item = DesignItem(f'{form}', test_case_widget, lb_scheme_widget, form,
                                      class_='ma-1',
                                      style_='background-color: #F8F8F8;'
                )
                self.design_list.children.append(new_item)
                create_dialog.v_model = False

                def remove_item(widget, event, data):
                    self.design_list.children.remove(new_item)
                    self.design_list.notify_change({'name': 'children', 'type': 'change'})

                new_item.btn.on_event('click', remove_item)
                new_item.on_event('click', new_item.update_chip)
                self.design_list.notify_change({'name': 'children', 'type': 'change'})

        create_close.on_event('click', close_click)
        create_add.on_event('click', add_click)

        def on_add_click(widget, event, data):
            with out:
                form.reset_form()
                create_dialog.v_model = True

        add_button.on_event('click', on_add_click)

        self.widget = v.Card(children=[
            v.CardText(children=[self.design_list]),
            v.CardActions(children=[v.Spacer(), add_button])
        ])

    def purge(self):
        self.design_list.children = []

    def design_space(self):
        test_case = self.test_case_widget.get_case()
        lb_scheme = self.lb_scheme_widget.get_case()

        output = {}
        for c in self.design_list.children:
            if c.relax:
                attrs = [getattr(lb_scheme, r).symb for r in c.relax]
                if c.srt:
                    output.update({tuple(attrs): (c.min, c.max)})
                else:
                    output.update({a: (c.min, c.max) for a in attrs})
            else:
                if hasattr(test_case, c.param):
                    attr = getattr(test_case, c.param)
                elif hasattr(lb_scheme, c.param):
                    attr = getattr(lb_scheme, c.param)
                    if isinstance(attr, SchemeVelocity):
                        attr = attr.symb
                if not isinstance(attr, sp.Symbol):
                    attr = c.param
                output.update({attr: (c.min, c.max)})
        return output