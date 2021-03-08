import ipyvuetify as v

from .pylbmwidget import out

import enum
from traitlets import List, UseEnum

class SaveType(enum.Enum):
    frequency = 'Frequency'
    steps = 'List of steps'
    step_period = 'Step period'
    times = 'List of times'
    time_period = 'Time period'

class SaveForm(v.Form):
    def __init__(self, fields):
        self.select_field = v.Select(label='Fields', v_model=None, items=fields, required=True, multiple=True)
        self.select_when = v.Select(label='When', v_model=None, items=[t.value for t in SaveType], required=True)

        self.select_field.observe(self.select_fields_rules, 'v_model')
        self.select_when.observe(self.select_when_rules, 'v_model')

        super().__init__(v_model='valid', children=[self.select_field, self.select_when,])

    def select_fields_rules(self, change):
        if self.select_field.v_model is None:
            self.select_field.rules = ['You must select at least one field']
            self.select_field.error = True
            self.v_model = False
        else:
            self.select_field.rules = []
            self.select_field.error = False
            self.v_model = True

    def select_when_rules(self, change):
        if self.select_when.v_model is None:
            self.select_when.rules = ['You must select one item indicating when to save the fields']
            self.select_when.error = True
            self.v_model = False
        else:
            self.select_when.rules = []
            self.select_when.error = False
            self.v_model = True

    def check_rules(self):
        self.select_fields_rules(None)
        self.select_when_rules(None)

    def reset_form(self):
        self.select_field.v_model = None
        self.select_field.rules = []
        self.select_field.error = False

        self.select_when.v_model = None
        self.select_when.rules = []
        self.select_when.error = False

        self.v_model = False

class SaveChip(v.Chip):
    fields = List()
    when = UseEnum(SaveType)

    def __init__(self, all_fields, **kwargs):
        self.form = SaveForm(all_fields)

        update_btn = v.Btn(children=['update'], color='success')
        close_btn = v.Btn(children=['close'], color='error')

        self.update_dialog = v.Dialog(
            width='500',
            v_model=False,
            children=[
                v.Card(children=[
                    v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                        "Update save configuration"
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
                    self.fields = self.form.select_field.v_model
                    self.when = SaveType(self.form.select_when.v_model)
                    self.children = [', '.join(self.form.select_field.v_model) + f' ({self.form.select_when.v_model})', self.update_dialog]
                    self.update_dialog.v_model = False

    def update_chip(self, widget, event, data):
        self.form.reset_form()
        self.form.select_field.v_model = self.fields
        self.form.select_when.v_model =  self.when.value
        self.update_dialog.v_model = True

class Save_widget:
    def __init__(self, all_fields):
        form = SaveForm(all_fields)

        create_add = v.Btn(children=['add'], color='success')
        create_close = v.Btn(children=['close'], color='error')

        create_dialog = v.Dialog(
            width='500',
            v_model=False,
            children=[
                v.Card(children=[
                    v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                        "New field save configuration"
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
                    new_chip = SaveChip(all_fields, fields=form.select_field.v_model, when=SaveType(form.select_when.v_model), children=[', '.join(form.select_field.v_model) + f' ({form.select_when.v_model})'], close=True)
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