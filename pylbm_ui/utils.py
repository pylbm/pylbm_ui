import ipyvuetify as v

from .mixin import *

class FloatField(v.TextField, FloatMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.observe(self.check, 'v_model')

    @property
    def value(self):
        return float(self.v_model)

    @value.setter
    def value(self, v):
        self.v_model = float(v)

class IntField(v.TextField, IntMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.observe(self.check, 'v_model')

    @property
    def value(self):
        return int(self.v_model)

    @value.setter
    def value(self, v):
        self.v_model = int(v)

class StrictlyPositiveIntField(IntField, StrictlyPositiveMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.observe(self.check, 'v_model')

class StrictlyPositiveFloatField(FloatField, StrictlyPositiveMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.observe(self.check, 'v_model')

class RelaxField(FloatField, PositiveMixin, BoundMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.observe(self.check, 'v_model')

TYPE_TO_WIDGET = {
    'integer': IntField,
    'number': FloatField,
    'scheme velocity': StrictlyPositiveFloatField,
    'relaxation parameter': RelaxField,
}

def schema_to_widgets(parameter_widget, data):
    schema = data.schema()
    required = schema['required']
    properties = schema['properties']

    widgets = {}
    for field in required:
        default = getattr(data, field)
        if hasattr(default, 'value'):
            default_value = default.value
            name = str(default.symb)
        else:
            default_value = default
            name = field

        data_type = properties[field].get('format', None)
        if data_type is None:
            data_type = properties[field]['type']

        if field not in parameter_widget:
            widgets[field] = TYPE_TO_WIDGET[data_type](label=name, v_model=default_value)
        else:
            widgets[field] = parameter_widget[field]
            widgets[field].v_model = default_value

    return widgets

def required_fields(data):
    schema = data.schema()
    required = schema['required']
    properties = schema['properties']

    fields = {}
    for field in required:
        default = getattr(data, field)
        if hasattr(default, 'value'):
            default_value = default.value
            name = str(default.symb)
        else:
            default_value = default
            name = field

        data_type = properties[field].get('format', None)
        if data_type is None:
            data_type = properties[field]['type']

        fields[field] = {'name': name, 'value': default_value, 'type': data_type}

    return fields