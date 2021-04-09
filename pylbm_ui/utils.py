import ipyvuetify as v
from .tab_widgets.pylbmwidget import out

def schema_to_widgets(parameter_widget, data):
    with out:
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
                widgets[field] = v.TextField(label=name, v_model=default_value, type='number')
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