import ipyvuetify as v

from ..utils import schema_to_widgets
from .pylbmwidget import Markdown, ParametersPanel, Tabs, out

class LB_scheme_widget:
    def __init__(self, cases, default_case):
        self.cases = cases
        case = v.Select(items=list(cases.keys()), v_model=default_case, label='LBM schemes')
        panels = v.ExpansionPanels(v_model=None, children=[ParametersPanel('Show parameters')])

        self.parameters = None
        description = Markdown()
        properties = v.Layout()

        tabs = Tabs(v_model=None, children=[v.Tab(children=['Description']),
                                            v.Tab(children=['Properties']),
                                            v.Tab(children=['Equivalent equations']),
                                            v.TabItem(children=[description]),
                                            v.TabItem(children=[properties]),
                                            v.TabItem(children=[]),
                                            ], right=True)

        self.widget = v.Row(children=[v.Col(children=[case, panels], sm=3),
                                      v.Col(children=[tabs])
        ])

        def change_param(change):
            pass

        def change_case(change):
            with out:
                v_model = tabs.v_model
                description.update_content(cases[case.v_model].description)
                tabs.children[4].children = [Markdown(cases[case.v_model].description)]
                self.parameters = schema_to_widgets(cases[case.v_model])
                panels.children[0].update(self.parameters.values())
                panels.children[0].bind(change_param)
                tabs.v_model = v_model

                if not tabs.viz:
                    tabs.show()
                    panels.children[0].show()

                change_param(None)

        case.observe(change_case, 'v_model')
        panels.children[0].bind(change_param)
        change_case(None)
        self.case = case
        self.panels = panels

    def get_case(self):
        select_case = self.cases[self.case.v_model]
        for k, v in self.parameters.items():
                setattr(select_case, k, float(v.v_model))
        return select_case
