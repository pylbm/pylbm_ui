import ipyvuetify as v

def schema_to_widgets(data):
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

        widgets[field] = v.TextField(label=name, v_model=default, type='number')

    return widgets