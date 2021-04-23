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
from .pylbmwidget import Markdown, ParametersPanel, out

class Test_case_widget:
    def __init__(self, cases, default_case):
        with out:
            self.default_cases = cases
            self.cases = copy.deepcopy(cases)
            self.parameters = {}

            self.select_case = v.Select(items=list(self.cases.keys()), v_model=default_case, label='Test cases')

            self.panels = v.ExpansionPanels(v_model=None, children=[ParametersPanel('Show parameters')])

            self.description = Markdown()
            plt.ioff()
            self.fig = plt.figure(figsize=(12,6))
            self.fig.canvas.header_visible = False

            tabs_content = [v.TabItem(children=[self.description]), v.TabItem(children=[self.fig.canvas])]
            self.tabs = v.Tabs(v_model=None,
                        children=[v.Tab(children=['Description']),
                                  v.Tab(children=['Reference results'])] + tabs_content)

            self.reset = v.Btn(children=['reset to default'], class_='d-none')

            self.menu = [self.select_case, self.panels, self.reset]
            self.main = [self.tabs]
            self.widget = v.Container(children=[v.Row(children=[v.Col(children=[self.select_case, self.panels], lg=400),
                                                                v.Col(children=[self.tabs])
                                                               ])
            ])

            self.reset.on_event('click', self.reset_btn)
            self.select_case.observe(self.change_case, 'v_model')
            self.panels.children[0].bind(self.change_param)
            self.change_case(None)

    def reset_btn(self, widget, event, data):
        with out:
            case = self.select_case.v_model
            self.cases[case] = copy.deepcopy(self.default_cases[case])
            self.change_case(None)

    def change_param(self, change):
        with out:

            v_model = self.panels.v_model
            for axe in self.fig.axes:
                self.fig.delaxes(axe)
            self.panels.v_model = v_model

            case = self.cases[self.select_case.v_model]
            default_case = self.default_cases[self.select_case.v_model]
            is_same = True
            for k, v in self.parameters.items():
                setattr(case, k, v.value)
                attr = getattr(default_case, k)
                if v.value != attr:
                    is_same = False

            if not is_same:
                self.reset.class_ = ''
            else:
                self.reset.class_ = 'd-none'

            if hasattr(case, 'plot_ref_solution'):
                case.plot_ref_solution(self.fig)
                self.fig.canvas.draw_idle()
                self.tabs.children[1].disabled = False
            else:
                self.tabs.children[1].disabled = True

    def change_case(self, change):
        with out:
            self.panels.children[0].unbind(self.change_param)
            v_model = self.tabs.v_model
            self.description.update_content(self.cases[self.select_case.v_model].description)
            self.parameters = schema_to_widgets(self.parameters, self.cases[self.select_case.v_model])
            self.panels.children[0].update(self.parameters.values())
            self.panels.children[0].bind(self.change_param)
            self.tabs.v_model = v_model

            self.change_param(None)

    def get_case(self, update_param=False):
        return self.cases[self.select_case.v_model]

