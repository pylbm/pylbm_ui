# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v
import copy

from ..utils import schema_to_widgets
from .pylbmwidget import Markdown, ParametersPanel, out
from .message import Message

class LB_scheme_widget:
    def __init__(self, tc, known_cases):
        self.known_cases = known_cases
        self.default_cases = {c.name: c for c in known_cases[tc.get_case()]}
        self.cases = {c.name: copy.copy(c) for c in known_cases[tc.get_case()]}
        default_case = list(self.cases.keys())[0]
        select_case = v.Select(items=list(self.cases.keys()), v_model=default_case, label='LBM schemes')
        panels = v.ExpansionPanels(v_model=None, children=[ParametersPanel('Show parameters')])

        self.parameters = {}
        description = Markdown()
        properties = v.Layout()
        eq_pde = v.Layout()

        reset = v.Btn(children=['reset to default'], class_='d-none')

        tabs = v.Tabs(v_model=0, children=[v.Tab(children=['Description']),
                                           v.Tab(children=['Properties']),
                                           v.Tab(children=['Equivalent equations']),
                                           v.TabItem(children=[description]),
                                           v.TabItem(children=[properties]),
                                           v.TabItem(children=[eq_pde]),
                                           ])

        self.widget = v.Row(children=[v.Col(children=[select_case, panels], sm=3),
                                      v.Col(children=[tabs])
        ])

        def change_param(change):
            reset.class_ = ''

        def change_tab(change):
            with out:
                case = self.cases[select_case.v_model]
                if tabs.v_model == 1 and not properties.children:
                    properties.children = [Message('Compute the properties of the scheme')]
                    properties.children = [case.get_information().vue()]
                if tabs.v_model == 2 and not eq_pde.children:
                    eq_pde.children = [Message('Compute the equivalent equations of the scheme')]
                    eq_pde.children = [case.get_eqpde().vue()]

        def change_test_case(change):
            with out:
                current_case = self.select_case.v_model
                self.default_cases = {c.name: c for c in known_cases[tc.get_case()]}
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
                properties.children = []
                eq_pde.children = []
                panels.children[0].update(self.parameters.values())
                panels.children[0].bind(change_param)
                tabs.v_model = v_model

                if tabs.v_model > 0:
                    change_tab(None)
                # if not tabs.viz:
                #     tabs.show()
                #     panels.children[0].show()

                change_param(None)
                reset.class_ = 'd-none'

        def reset_btn(widget, event, data):
            with out:
                self.cases[select_case.v_model] = copy.deepcopy(self.default_cases[select_case.v_model])
                change_case(None)

        reset.on_event('click', reset_btn)

        tabs.observe(change_tab, 'v_model')
        select_case.observe(change_case, 'v_model')

        tc.select_case.observe(change_test_case, 'v_model')

        panels.children[0].bind(change_param)
        change_case(None)
        self.main = [tabs]
        self.menu = [select_case, panels, reset]
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
