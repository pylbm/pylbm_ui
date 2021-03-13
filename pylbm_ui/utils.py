import ipyvuetify as v

def schema_to_widgets(parameter_widget, data):
    schema = data.schema()
    required = schema['required']
    properties = schema['properties']

    widgets = {}
    for field in required:
        property = properties[field]
        name = property['title']
        default = getattr(data, field)

        data_type = property.get('format', None)
        if data_type is None:
            data_type = property['type']

        if field not in parameter_widget:
            widgets[field] = v.TextField(label=name, v_model=default, type='number')
        else:
            widgets[field] = parameter_widget[field]
            widgets[field].v_model = default

    return widgets

def required_fields(data):
    schema = data.schema()
    required = schema['required']
    properties = schema['properties']

    fields = {}
    for field in required:
        property = properties[field]
        name = property['title']
        default = getattr(data, field)

        data_type = property.get('format', None)
        if data_type is None:
            data_type = property['type']

        fields[field] = {'name': name, 'value': default, 'type': data_type}

    return fields