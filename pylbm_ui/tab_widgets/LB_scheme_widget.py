import ipyvuetify as v

from ..utils import schema_to_widgets
from .pylbmwidget import Markdown, ParametersPanel, Tabs, out

class LB_scheme_widget:
    def __init__(self, tc, known_cases):
        self.known_cases = known_cases
        self.cases = {c.name: c for c in known_cases[tc.get_case()]}
        default_case = list(self.cases.keys())[0]
        select_case = v.Select(items=list(self.cases.keys()), v_model=default_case, label='LBM schemes')
        panels = v.ExpansionPanels(v_model=None, children=[ParametersPanel('Show parameters')])

        self.parameters = {}
        description = Markdown()
        properties = v.Layout()
        eq_pde = v.Layout()

        tabs = Tabs(v_model=None, children=[v.Tab(children=['Description']),
                                            v.Tab(children=['Properties']),
                                            v.Tab(children=['Equivalent equations']),
                                            v.TabItem(children=[description]),
                                            v.TabItem(children=[properties]),
                                            v.TabItem(children=[eq_pde]),
                                            ], right=True)

        self.widget = v.Row(children=[v.Col(children=[select_case, panels], sm=3),
                                      v.Col(children=[tabs])
        ])

        def change_param(change):
            pass

        def change_test_case(change):
            with out:
                current_case = self.select_case.v_model
                self.cases = {c.name: c for c in known_cases[tc.get_case()]}
                if current_case not in self.cases.keys():
                    current_case = list(self.cases.keys())[0]

                select_case.items = list(self.cases.keys())
                select_case.v_model = current_case
                change_case(None)

        def change_case(change):
            with out:
                v_model = tabs.v_model
                case = self.cases[select_case.v_model]
                self.parameters = schema_to_widgets(self.parameters, case)
                description.update_content(case.description)
                # properties.children = [case.get_information().vue()]
                # eq_pde.children = [case.get_eqpde().vue()]
                panels.children[0].update(self.parameters.values())
                panels.children[0].bind(change_param)
                tabs.v_model = v_model

                # if not tabs.viz:
                #     tabs.show()
                #     panels.children[0].show()

                change_param(None)

        select_case.observe(change_case, 'v_model')

        tc.select_case.observe(change_test_case, 'v_model')

        panels.children[0].bind(change_param)
        change_case(None)
        self.select_case = select_case
        self.panels = panels

    def get_case(self):
        case = self.cases[self.select_case.v_model]
        for k, v in self.parameters.items():
            attr = getattr(case, k)
            if hasattr(attr, 'value'):
                attr.value = v.value
            else:
                attr = v.value
        return case
