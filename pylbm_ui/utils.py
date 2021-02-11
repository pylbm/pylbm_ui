from ipywidgets import IntText, FloatText, Text, Layout, BoundedFloatText

WIDGET_MAP = {
    'integer': lambda default, description: IntText(value=default,
                                                    description=description,
                                                    layout=Layout(width='auto')),
    'number': lambda default, description: FloatText(value=default,
                                                     description=description,
                                                     layout=Layout(width='auto')),
    'string': lambda default, description: Text(value=default,
                                                description=description,
                                                layout=Layout(width='auto')),
    'relaxation parameter': lambda default, description: BoundedFloatText(value=default,
                                                                          min=0., max=2.0, step=0.01,
                                                                          description=description,
                                                                          layout=Layout(width='auto')),
    # bool: (wid.Checkbox, 'value'),
    # list: (wid.Dropdown, 'options'),
    # tuple: (wid.Dropdown, 'options'),
    # set: (wid.Dropdown, 'options')
}


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

        widgets[field] = WIDGET_MAP[data_type](default, name)

    return widgets