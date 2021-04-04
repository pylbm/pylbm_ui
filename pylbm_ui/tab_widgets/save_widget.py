import ipyvuetify as v

from .pylbmwidget import out, debug_widget

import re
import enum
from traitlets import List, UseEnum, Unicode

class SaveType(enum.Enum):
    frequency = 'Frequency'
    steps = 'List of steps'
    step_period = 'Step period'
    times = 'List of times'
    time_period = 'Time period'

class SaveForm(v.Form):
    def __init__(self, fields):
        self.fields = fields
        self.select_field = v.Select(label='Fields', v_model=[], items=['all'] + fields, required=True, multiple=True)
        self.select_when = v.Select(label='When', v_model=None, items=[t.value for t in SaveType], required=True)
        self.when_properties = v.TextField(label='when save the fields?', v_model=None, required=True)
        self.select_field.observe(self.select_fields_rules, 'v_model')
        self.select_field.observe(self.select_fields_all, 'v_model')
        self.select_when.observe(self.select_when_rules, 'v_model')
        self.select_when.observe(self.when_properties_rules, 'v_model')
        self.when_properties.observe(self.when_properties_rules, 'v_model')

        super().__init__(v_model='valid', children=[self.select_field, self.select_when,self.when_properties,])

    def select_fields_all(self, change):
        if 'all' in self.select_field.v_model:
            self.select_field.v_model = self.fields

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

    def when_properties_rules(self, change):
        if self.select_when.v_model in ['Frequency', 'Step period']:
            try:
                int(self.when_properties.v_model)
                self.when_properties.rules = []
                self.when_properties.error = False
                self.v_model = True
            except:
                self.when_properties.rules = ['You must enter an integer']
                self.when_properties.error = True
                self.v_model = False
        if self.select_when.v_model == 'List of steps':
            try:
                int_regexp = "^\d+(-\d+)?(?:,\d+(?:-\d+)?)*$"
                clean_str = self.when_properties.v_model.replace(' ', '')
                if not re.match(int_regexp, clean_str):
                    raise

                for r in clean_str.split(','):
                    steps = r.split('-')
                    if len(steps) == 2:
                        if int(steps[1]) <= int(steps[0]):
                            raise

                self.when_properties.rules = []
                self.when_properties.error = False
                self.v_model = True
            except:
                self.when_properties.rules = ['You must enter a list of integers. For example: 1, 2-4, 6']
                self.when_properties.error = True
                self.v_model = False
        if self.select_when.v_model == 'List of times':
            try:
                list(map(float, self.when_properties.v_model.split(',')))
                self.when_properties.rules = []
                self.when_properties.error = False
                self.v_model = True
            except:
                self.when_properties.rules = ['You must enter a list of floats. For example: 0.1, 0.25, 0.6']
                self.when_properties.error = True
                self.v_model = False
        if self.select_when.v_model == 'Time period':
            try:
                float(self.when_properties.v_model)
                self.when_properties.rules = []
                self.when_properties.error = False
                self.v_model = True
            except:
                self.when_properties.rules = ['You must enter a float.']
                self.when_properties.error = True
                self.v_model = False

    def check_rules(self):
        self.select_fields_rules(None)
        self.select_when_rules(None)
        self.when_properties_rules(None)

    def reset_form(self):
        self.select_field.v_model = []
        self.select_field.rules = []
        self.select_field.error = False

        self.select_when.v_model = None
        self.select_when.rules = []
        self.select_when.error = False

        self.when_properties.v_model = None
        self.when_properties.rules = []
        self.when_properties.error = False

        self.v_model = False

    def __str__(self):
        return ', '.join(self.select_field.v_model) + f' ({self.select_when.v_model}: {self.when_properties.v_model})'

class SaveItem(v.ListItem):
    fields = List()
    when = UseEnum(SaveType)
    when_properties = Unicode()

    def __init__(self, all_fields, content, **kwargs):
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
                self.fields = self.form.select_field.v_model
                self.when = SaveType(self.form.select_when.v_model)
                self.when_properties = self.form.when_properties.v_model
                self.content.children = [f'{self.form}']
                self.update_dialog.v_model = False

    def update_item(self, widget, event, data):
        self.form.reset_form()
        self.form.select_field.v_model = self.fields
        self.form.select_when.v_model =  self.when.value
        self.form.when_properties.v_model =  self.when_properties
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

        self.request_list = v.List(children=[])
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
                new_item = SaveItem(all_fields,
                                    f'{form}',
                                    fields=form.select_field.v_model,
                                    when=SaveType(form.select_when.v_model),
                                    when_properties=form.when_properties.v_model,
                                    class_='ma-1',
                                    style_='background-color: #F8F8F8;'
                                    )

                self.request_list.children.append(new_item)
                create_dialog.v_model = False

                def close_chip(widget, event, data):
                    self.request_list.children.remove(new_item)
                    self.request_list.notify_change({'name': 'children', 'type': 'change'})

                new_item.btn.on_event('click', close_chip)
                new_item.on_event('click', new_item.update_item)
                self.request_list.notify_change({'name': 'children', 'type': 'change'})

        create_close.on_event('click', close_click)
        create_add.on_event('click', add_click)

        def on_add_click(widget, event, data):
            form.reset_form()
            create_dialog.v_model = True

        add_button.on_event('click', on_add_click)

        self.widget = v.Card(children=[
            v.CardText(children=[self.request_list]),
            v.CardActions(children=[v.Spacer(), add_button])
        ])

    def get_save_time(self, dt, final_time):
        nsteps = int(final_time/dt)
        output = {}

        def add_ite(ite, fields):
            i = output.get(ite, None)
            if i:
                output.update(set(fields))
            else:
                output[ite] = set(fields)

        for c in self.request_list.children:
            if c.when == SaveType.frequency:
                freq = int(c.when_properties)
                for i in range(freq):
                    ite = nsteps * (i+1)/freq
                    add_ite(ite, c.fields)
            elif c.when == SaveType.steps:
                clean_str = c.when_properties.replace(' ', '')
                for r in clean_str.split(','):
                    steps = r.split('-')
                    if len(steps) == 2:
                        for ite in range(int(steps[0]), int(steps[1])+1):
                            add_ite(ite, c.fields)
                    else:
                        add_ite(int(steps[0]), c.fields)
            elif c.when == SaveType.step_period:
                step = int(c.when_properties)
                for ite in range(0, nsteps, step):
                    add_ite(ite, c.fields)
            elif c.when == SaveType.times:
                clean_str = c.when_properties.replace(' ', '')
                for r in clean_str.split(','):
                    ite = int(float(r)/dt)
                    add_ite(ite, c.fields)
            elif c.when == SaveType.time_period:
                step = int(float(c.when_properties)/dt)
                print(step, nsteps, dt, final_time)
                for ite in range(0, nsteps, step):
                    add_ite(ite, c.fields)

        return output
