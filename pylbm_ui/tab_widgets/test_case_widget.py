import matplotlib.pyplot as plt
import ipyvuetify as v

from ..utils import schema_to_widgets
from .pylbmwidget import Markdown, ParametersPanel, Tabs, out

class Test_case_widget:

    def __init__(self, cases, default_case):

        self.cases = cases
        self.parameters = {}

        select_case = v.Select(items=list(cases.keys()), v_model=default_case, label='Test cases')

        panels = v.ExpansionPanels(v_model=None, children=[ParametersPanel('Show parameters')])

        description = Markdown()
        plt.ioff()
        fig = plt.figure(figsize=(12,6))
        fig.canvas.header_visible = False

        tabs_content = [v.TabItem(children=[description]), v.TabItem(children=[fig.canvas])]
        tabs = Tabs(v_model=None,
                     children=[v.Tab(children=['Description']),
                               v.Tab(children=['Reference results'])] + tabs_content, right=True)
        self.widget = v.Row(children=[v.Col(children=[select_case, panels], sm=3),
                                      v.Col(children=[tabs])
        ])

        def change_param(change):
            v_model = panels.v_model
            for axe in fig.axes:
                fig.delaxes(axe)
            panels.v_model = v_model

            case = cases[select_case.v_model]
            for k, v in self.parameters.items():
                setattr(case, k, float(v.v_model))
            if hasattr(case, 'plot_ref_solution'):
                case.plot_ref_solution(fig)
                fig.canvas.draw_idle()

        def change_case(change):
            with out:
                panels.children[0].unbind(change_param)
                v_model = tabs.v_model
                description.update_content(cases[select_case.v_model].description)
                self.parameters = schema_to_widgets(self.parameters, cases[select_case.v_model])
                panels.children[0].update(self.parameters.values())
                panels.children[0].bind(change_param)
                tabs.v_model = v_model

                if not tabs.viz:
                    tabs.show()
                    panels.children[0].show()

                change_param(None)
                panels.children[0].bind(change_param)

        select_case.observe(change_case, 'v_model')
        panels.children[0].bind(change_param)
        change_case(None)

        self.select_case = select_case

    def get_case(self, update_param=False):
        return self.cases[self.select_case.v_model]
