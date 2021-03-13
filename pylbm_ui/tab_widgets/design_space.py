import ipyvuetify as v

from .pylbmwidget import out

import enum
from traitlets import Unicode, Float, List

class DesignForm(v.Form):
    def __init__(self, params, relax_params):
        self.params = params
        self.select_param = v.Select(label='Parameters', v_model=None, items=sorted(params), multiple=False, required=True)
        self.select_relax = v.Select(label='Relaxation parameters', v_model=[], items=sorted(relax_params), multiple=True, required=True, class_='d-none')
        self.min = v.TextField(label='Enter the minimum', v_model=None, required=True, class_='d-none')
        self.max = v.TextField(label='Enter the maximum', v_model=None, required=True, class_='d-none')

        self.select_param.observe(self.select_param_changed, 'v_model')
        self.select_relax.observe(self.select_relax_rules, 'v_model')
        self.min.observe(self.minmax_rules, 'v_model')
        self.max.observe(self.minmax_rules, 'v_model')

        super().__init__(v_model='valid', children=[self.select_param, self.select_relax, self.min, self.max])

    def select_param_changed(self, change):
        with out:
            if self.select_param.v_model:
                if self.select_param.v_model == 'relaxation parameters':
                    self.min.v_model = 1
                    self.max.v_model = 1
                    self.select_relax.class_ = ''
                else:
                    self.min.v_model = self.params[self.select_param.v_model]
                    self.max.v_model = self.params[self.select_param.v_model]
                    self.select_relax.class_ = 'd-none'
                    self.select_relax.v_model = []
                self.min.class_ = ''
                self.max.class_ = ''
                self.min.notify_change({'name': 'v_model', 'type': 'change'})
                self.max.notify_change({'name': 'v_model', 'type': 'change'})

    def select_relax_rules(self, change):
        with out:
            if self.select_param.v_model == 'relaxation parameters':
                print(self.select_relax.v_model)
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
            return ', '.join(self.select_relax.v_model) + f'(min: {self.min.v_model}, max: {self.max.v_model})'
        else:
            return f'{self.select_param.v_model}(min: {self.min.v_model}, max: {self.max.v_model})'

class DesignChip(v.Chip):
    param = Unicode()
    relax = List()
    min = Float()
    max = Float()

    def __init__(self, parameters, relax_parameters, **kwargs):
        with out:
            self.form = DesignForm(parameters, relax_parameters)

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

            children = kwargs.get('children', [])
            children.append(self.update_dialog)
            kwargs.pop('children')
            super().__init__(children=children, **kwargs)

    def close_click(self, widget, event, data):
        self.update_dialog.v_model = False

    def update_click(self, widget, event, data):
        with out:
            self.form.check_rules()

            if self.form.v_model:
                self.param = self.form.select_param.v_model
                self.relax = self.form.select_relax.v_model
                self.min = float(self.form.min.v_model)
                self.max = float(self.form.max.v_model)
                self.children = [f'{self.form}', self.update_dialog]
                self.update_dialog.v_model = False

    def update_chip(self, widget, event, data):
        with out:
            self.form.reset_form()
            self.form.select_param.v_model = self.param
            self.form.select_relax.v_model = self.relax
            self.form.min.v_model =  self.min
            self.form.max.v_model =  self.max
            self.update_dialog.v_model = True

class Design_widget:
    def __init__(self, parameters, relax_parameters):
        form = DesignForm(parameters, relax_parameters)

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

        chip_group = v.ChipGroup(children=[], column=True)
        add_button = v.Btn(children=[v.Icon(children=['mdi-plus']), create_dialog], fab=True, color='pink', small=True, icon=True)

        def close_click(widget, event, data):
            create_dialog.v_model = False

        def add_click(widget, event, data):
            with out:
                form.check_rules()

                if form.v_model:
                    new_chip = DesignChip(parameters, relax_parameters,
                                        param=form.select_param.v_model,
                                        relax=form.select_relax.v_model,
                                        min=float(form.min.v_model),
                                        max=float(form.max.v_model),
                                        children=[f'{form}']
                                        , close=True)
                    new_chip_index = len(chip_group.children)
                    chip_group.children.append(new_chip)
                    create_dialog.v_model = False

                    def close_chip(widget, event, data):
                        chip_group.children.remove(widget)
                        chip_group.notify_change({'name': 'children', 'type': 'change'})

                    new_chip.on_event('click:close', close_chip)
                    new_chip.on_event('click', new_chip.update_chip)
                    chip_group.notify_change({'name': 'children', 'type': 'change'})

        create_close.on_event('click', close_click)
        create_add.on_event('click', add_click)

        def on_add_click(widget, event, data):
            with out:
                form.reset_form()
                create_dialog.v_model = True

        add_button.on_event('click', on_add_click)

        self.widget = v.Card(children=[
            v.CardText(children=[chip_group]),
            v.CardActions(children=[v.Spacer(), add_button])
        ])