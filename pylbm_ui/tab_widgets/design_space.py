import ipyvuetify as v

from .pylbmwidget import out

import enum
import sympy as sp
from traitlets import Unicode, Float, List, Bool

from schema.utils import SchemeVelocity, RelaxationParameterFinal

from .dialog_form import Form, Item, Dialog, add_rule
from ..utils import required_fields, FloatField, RelaxField

class DesignForm(Form):
    def __init__(self, test_case_widget, lb_scheme_widget, **kwargs):
        self.test_case_widget, self.lb_scheme_widget = test_case_widget, lb_scheme_widget
        self.params, self.relax_params = None, None

        self.select_param = v.Select(label='Parameters', v_model=None, items=[])
        self.select_relax = v.Select(label='Relaxation parameters', v_model=[], items=[], multiple=True, class_='d-none')
        self.srt_relax = v.Switch(label='Single relaxation time', v_model=True, class_='d-none')
        self.minmax = v.Layout()

        self.update_select_fields(None)

        test_case_widget.select_case.observe(self.update_select_fields, 'v_model')
        lb_scheme_widget.select_case.observe(self.update_select_fields, 'v_model')

        self.select_param.observe(self.select_param_changed, 'v_model')
        self.select_relax.observe(self.select_relax_rules, 'v_model')
        self.select_relax.observe(self.select_relax_all, 'v_model')

        self.fields = [self.select_param, self.select_relax, self.srt_relax, self.minmax]

        super().__init__(v_model='valid', children=self.fields)

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
                    self.minmax.children = [
                        RelaxField(label='Enter the minimum', v_model=1),
                        RelaxField(label='Enter the maximum', v_model=1)
                    ]
                    self.select_relax.class_ = ''
                    self.srt_relax.class_ = ''
                else:
                    value = self.params[self.select_param.v_model]
                    self.minmax.children = [
                        FloatField(label='Enter the minimum', v_model=value),
                        FloatField(label='Enter the maximum', v_model=value)
                    ]
                    self.select_relax.class_ = 'd-none'
                    self.srt_relax.class_ = 'd-none'
                    self.select_relax.v_model = []

                for c in self.minmax.children:
                    c.observe(self.minmax_rules, 'v_model')
                    c.observe(self.minmax_rules, 'v_model')

    def select_relax_all(self, change):
        if 'all' in self.select_relax.v_model:
            self.select_relax.v_model = list(self.relax_params.keys())

    @add_rule
    def select_relax_rules(self, change):
        with out:
            if self.select_param.v_model == 'relaxation parameters':
                if self.select_relax.v_model == []:
                    self.select_relax.rules = ['You must select at least one relaxation parameter']
                    self.select_relax.error = True
                    return
                else:
                    self.select_relax.rules = []
                    self.select_relax.error = False

    @add_rule
    def minmax_rules(self, change):
        min_widget, max_widget = self.minmax.children
        min, max = min_widget.value, max_widget.value
        if min == max:
            min_widget.rules = ['Min must be different from Max']
            min_widget.error = True
            max_widget.rules = ['Max must be different from Min']
            max_widget.error = True
            self.minmax.error = True
            return
        elif min > max:
            min_widget.rules = ['Min must be lower than Max']
            min_widget.error = True
            max_widget.rules = ['Max must be greater than Min']
            max_widget.error = True
            self.minmax.error = True
            return
        else:
            min_widget.check(None)
            max_widget.check(None)
            self.minmax.error = min_widget.error | max_widget.error

    def reset_form(self):
        super().reset_form()
        self.select_relax.class_ = 'd-none'
        self.srt_relax.class_ = 'd-none'
        self.srt_relax.v_model = True
        self.minmax.children = []

class DesignItem(Item):
    form_class = DesignForm
    update_text = 'Update field range configuration'

    param = Unicode()
    relax = List()
    srt = Bool()
    min = Float()
    max = Float()

    def __init__(self, test_case_widget, lb_scheme_widget, **kwargs):
        super().__init__(test_case_widget, lb_scheme_widget, **kwargs)
        self.content.children = [f'{self}']

    def form2field(self):
        self.param = self.form.select_param.v_model
        self.relax = self.form.select_relax.v_model
        self.srt = self.form.srt_relax.v_model
        self.min = self.form.minmax.children[0].value
        self.max = self.form.minmax.children[1].value

    def field2form(self):
        self.form.select_param.v_model = self.param
        self.form.select_relax.v_model = self.relax
        self.form.srt_relax.v_model = self.srt
        self.form.minmax.children[0].value =  self.min
        self.form.minmax.children[1].value =  self.max

    def __str__(self):
        if self.param == 'relaxation parameters':
            return ', '.join(self.relax) + f' (srt: {self.srt}, min: {self.min}, max: {self.max})'
        else:
            return f'{self.param} (min: {self.min}, max: {self.max})'

class Design_widget(Dialog):
    item_class = DesignItem
    new_text = "New field range configuration"

    def __init__(self, test_case_widget, lb_scheme_widget):
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget
        super().__init__(test_case_widget, lb_scheme_widget)

    def create_item(self):
        return DesignItem(self.test_case_widget, self.lb_scheme_widget,
                    param = self.form.select_param.v_model,
                    relax = self.form.select_relax.v_model,
                    srt = self.form.srt_relax.v_model,
                    min = self.form.minmax.children[0].value,
                    max = self.form.minmax.children[1].value,
                    class_='ma-1',
                    style_='background-color: #F8F8F8;'
        )

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