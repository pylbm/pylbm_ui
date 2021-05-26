# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v

from .pylbmwidget import out, debug_widget

import re
import enum
from traitlets import List, UseEnum, Unicode

from .dialog_form import Form, Item, Dialog, add_rule


class SaveType(enum.Enum):
    frequency = 'Frequency'
    steps = 'List of steps'
    step_period = 'Step period'
    times = 'List of times'
    time_period = 'Time period'


class SaveForm(Form):
    def __init__(self, fields, *args, **kwargs):
        self.select_field = v.Select(
            label='Fields', v_model=[],
            items=['all'] + fields, required=True, multiple=True
        )
        self.select_when = v.Select(
            label='When', v_model=None,
            items=[t.value for t in SaveType],
            required=True
        )
        self.when_properties = v.TextField(
            label='when save the fields?', v_model=None, required=True
        )

        def select_fields_all(change):
            if 'all' in self.select_field.v_model:
                self.select_field.v_model = fields

        self.select_field.observe(self.select_fields_rules, 'v_model')
        self.select_field.observe(select_fields_all, 'v_model')
        self.select_when.observe(self.select_when_rules, 'v_model')
        self.select_when.observe(self.when_properties_rules, 'v_model')
        self.when_properties.observe(self.when_properties_rules, 'v_model')

        self.fields = [
            self.select_field, self.select_when, self.when_properties
        ]

        super().__init__(
            v_model='valid',
            children=[
                self.select_field, self.select_when, self.when_properties,
            ]
        )

    def update_fields(self, new_fields):
        self.select_field.items = ['all'] + new_fields

    @add_rule
    def select_fields_rules(self, change):
        if self.select_field.v_model is None:
            self.select_field.rules = ['You must select at least one field']
            self.select_field.error = True
            return
        else:
            self.select_field.rules = []
            self.select_field.error = False

    @add_rule
    def select_when_rules(self, change):
        if self.select_when.v_model is None:
            self.select_when.rules = [
                'You must select one item indicating when to save the fields'
            ]
            self.select_when.error = True
            return
        else:
            self.select_when.rules = []
            self.select_when.error = False

    @add_rule
    def when_properties_rules(self, change):
        if self.select_when.v_model in ['Frequency', 'Step period']:
            try:
                int(self.when_properties.v_model)
                self.when_properties.rules = []
                self.when_properties.error = False
            except:
                self.when_properties.rules = ['You must enter an integer']
                self.when_properties.error = True
                return
        elif self.select_when.v_model == 'List of steps':
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
            except:
                self.when_properties.rules = [
                    'You must enter a list of integers. For example: 1, 2-4, 6'
                ]
                self.when_properties.error = True
                return
        elif self.select_when.v_model == 'List of times':
            try:
                list(map(float, self.when_properties.v_model.split(',')))
                self.when_properties.rules = []
                self.when_properties.error = False
            except:
                self.when_properties.rules = [
                    'You must enter a list of floats. For example: 0.1, 0.25, 0.6'
                ]
                self.when_properties.error = True
                return
        elif self.select_when.v_model == 'Time period':
            try:
                float(self.when_properties.v_model)
                self.when_properties.rules = []
                self.when_properties.error = False
            except:
                self.when_properties.rules = ['You must enter a float.']
                self.when_properties.error = True
                return


class SaveItem(Item):
    form_class = SaveForm
    update_text = 'Update save configuration'

    field_list = List()
    when = UseEnum(SaveType)
    when_properties = Unicode()

    def __init__(self, all_fields, **kwargs):
        super().__init__(all_fields, **kwargs)
        self.content.children = [f'{self}']

    def form2field(self):
        self.field_list = self.form.select_field.v_model
        self.when = SaveType(self.form.select_when.v_model)
        self.when_properties = self.form.when_properties.v_model

    def field2form(self):
        self.form.select_field.v_model = self.field_list
        self.form.select_when.v_model = self.when.value
        self.form.when_properties.v_model = self.when_properties

    def __str__(self):
        return ', '.join(self.field_list) + f' ({self.when.value}: {self.when_properties})'


class Save_widget(Dialog):
    item_class = SaveItem
    new_text = "New save configuration"

    def __init__(self, all_fields):
        with out:
            self.all_fields = all_fields
            super().__init__(all_fields)

    def update_fields(self, new_fields):
        self.all_fields = new_fields
        self.form.update_fields(new_fields)

    def create_item(self):
        return SaveItem(
            self.all_fields,
            field_list=self.form.select_field.v_model,
            when=SaveType(self.form.select_when.v_model),
            when_properties=self.form.when_properties.v_model,
            class_='ma-1',
            style_='background-color: #F8F8F8;'
        )

    def get_save_time(self, dt, final_time):
        nsteps = int(final_time/dt)
        output = {}

        def add_ite(ite, fields):
            i = output.get(ite, None)
            if i:
                output.update(set(fields))
            else:
                output[ite] = set(fields)

        for c in self.item_list.children:
            if c.when == SaveType.frequency:
                freq = int(c.when_properties)
                for i in range(freq+1):
                    ite = int(nsteps * i / freq)
                    add_ite(ite, c.field_list)
            elif c.when == SaveType.steps:
                clean_str = c.when_properties.replace(' ', '')
                for r in clean_str.split(','):
                    steps = r.split('-')
                    if len(steps) == 2:
                        for ite in range(int(steps[0]), int(steps[1])+1):
                            add_ite(ite, c.field_list)
                    else:
                        add_ite(int(steps[0]), c.field_list)
            elif c.when == SaveType.step_period:
                step = int(c.when_properties)
                for ite in range(0, nsteps+1, step):
                    add_ite(ite, c.field_list)
            elif c.when == SaveType.times:
                clean_str = c.when_properties.replace(' ', '')
                for r in clean_str.split(','):
                    ite = int(float(r)/dt)
                    add_ite(ite, c.field_list)
            elif c.when == SaveType.time_period:
                step = int(float(c.when_properties)/dt)
                for ite in range(0, nsteps+1, step):
                    add_ite(ite, c.field_list)

        return output
