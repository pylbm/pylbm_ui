import ipyvuetify as v
import markdown
import ipywidgets as widgets

class parametric_widget:
    def __init__(self):
        default_layout = widgets.Layout(width='90%')

        pause = widgets.ToggleButton(value=False,
                            description='Pause',
                            disabled=True,
        )
        start = widgets.ToggleButton(value=False,
                       description='Start',
                       button_style='success',
        )
        progress = widgets.FloatProgress(value=0.0, min=0.0, max=1.0,
                                 layout=widgets.Layout(width='80%')
        )

        design_space = widgets.VBox([widgets.Dropdown(options=["duration",markdown.markdown("$\delta x$")], layout=default_layout),
                                     widgets.FloatText(description='min',
                                                       style={'description_width': '50px'},
                                                       layout=default_layout),
                                     widgets.FloatText(description='max',
                                                       style={'description_width': '50px'},
                                                       layout=default_layout),
                                     widgets.HBox([widgets.Button(description='clear', button_style='danger'),
                                                  widgets.Button(description='remove', button_style='warning'),
                                                  widgets.Button(description='add', button_style='success'),
                                    ])
        ])

        responses = widgets.VBox([widgets.Dropdown(options=["duration","$\delta x$"], layout=default_layout),
                                  widgets.HBox([widgets.Button(description='clear', button_style='danger'),
                                                widgets.Button(description='remove', button_style='warning'),
                                                widgets.Button(description='add', button_style='success'),
                                  ])
        ])

        methods = widgets.FloatText(description='nb points',
                                    style={'description_width': '50px'},
                                    layout=default_layout)

        left_panel = widgets.VBox([widgets.HTML(value='<u><b>Study name</u></b>'),
                           widgets.Text(value='PS0',
                                layout=default_layout
                            ),
                           widgets.HTML(value='<u><b>Select simulation</u></b>'),
                           widgets.Button(description='update simulation list'),
                           widgets.HTML(value='<u><b>Settings</u></b>'),
                           widgets.Accordion(children=[design_space],
                                     _titles={0: 'Define design space'},
                                     selected_index=None,
                                     layout=default_layout),
                           widgets.Accordion(children=[responses],
                                     _titles={0: 'Select responses'},
                                     selected_index=None,
                                     layout=default_layout),
                           widgets.Accordion(children=[methods],
                                     _titles={0: 'Methods'},
                                     selected_index=None,
                                     layout=default_layout),
                            ],
                           layout=widgets.Layout(align_items='center', margin= '10px')
        )

        right_panel = widgets.Tab(_titles= {0: 'Post-treatment'},
        )

        self.widget = widgets.VBox([widgets.HBox([start, pause, progress]),
                            widgets.GridspecLayout(1, 4)])
        self.widget.children[1][0, 0] = left_panel
        self.widget.children[1][0, 1:] = right_panel
