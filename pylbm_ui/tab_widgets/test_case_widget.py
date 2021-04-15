# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import matplotlib.pyplot as plt
import ipyvuetify as v
import copy

from ..utils import schema_to_widgets
from .pylbmwidget import Markdown, ParametersPanel, Tabs, out

class Test_case_widget:
    def __init__(self, cases, default_case):
        with out:
            self.default_cases = cases
            self.cases = copy.deepcopy(cases)
            self.parameters = {}

            select_case = v.Select(items=list(self.cases.keys()), v_model=default_case, label='Test cases')

            panels = v.ExpansionPanels(v_model=None, children=[ParametersPanel('Show parameters')])

            description = Markdown()
            plt.ioff()
            fig = plt.figure(figsize=(12,6))
            fig.canvas.header_visible = False

            tabs_content = [v.TabItem(children=[description]), v.TabItem(children=[fig.canvas])]
            tabs = Tabs(v_model=None,
                        children=[v.Tab(children=['Description']),
                                  v.Tab(children=['Reference results'])] + tabs_content)

            reset = v.Btn(children=['reset to default'], class_='d-none')

            self.menu = [select_case, panels, reset]
            self.main = [tabs]
            self.widget = v.Container(children=[v.Row(children=[v.Col(children=[select_case, panels], lg=400),
                                                                v.Col(children=[tabs])
                                                               ])
            ])

            def change_param(change):
                reset.class_ = ''
                v_model = panels.v_model
                for axe in fig.axes:
                    fig.delaxes(axe)
                panels.v_model = v_model

                case = self.cases[select_case.v_model]
                for k, v in self.parameters.items():
                    setattr(case, k, v.value)
                if hasattr(case, 'plot_ref_solution'):
                    case.plot_ref_solution(fig)
                    fig.canvas.draw_idle()
                    tabs.children[1].disabled = False
                else:
                    tabs.children[1].disabled = True

            def change_case(change):
                panels.children[0].unbind(change_param)
                v_model = tabs.v_model
                description.update_content(self.cases[select_case.v_model].description)
                self.parameters = schema_to_widgets(self.parameters, self.cases[select_case.v_model])
                panels.children[0].update(self.parameters.values())
                panels.children[0].bind(change_param)
                tabs.v_model = v_model

                if not tabs.viz:
                    tabs.show()
                    panels.children[0].show()

                change_param(None)
                panels.children[0].bind(change_param)
                reset.class_ = 'd-none'

            def reset_btn(widget, event, data):
                with out:
                    self.cases[select_case.v_model] = copy.deepcopy(self.default_cases[select_case.v_model])
                    change_case(None)

            reset.on_event('click', reset_btn)
            select_case.observe(change_case, 'v_model')
            panels.children[0].bind(change_param)
            change_case(None)

            self.select_case = select_case
            self.panels = panels

    def get_case(self, update_param=False):
        return self.cases[self.select_case.v_model]
