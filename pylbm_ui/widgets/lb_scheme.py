# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v
import copy

from ..utils import schema_to_widgets
from .debug import debug
from .pylbmwidget import Markdown, ParametersPanel
from .message import Message


@debug
class LBSchemeWidget:
    def __init__(self, test_case, known_cases):
        """
        Widget definition for lattice Boltzmann schemes.

        Parameters
        ==========

        - test_case:
            the selected test case.

        - known_cases: dict
            A dictionary of all known cases
            the keys are an instance of a test case
            the values are a list of available lattice Boltzmann schemes for this test case

        This widget is composed by a menu where you can Choose the lb scheme and
        modify its default parameters. If you change any of the parameters, you will
        see a reset button to revover the default parameters of this scheme.

        This widget is also composed by a main widget where we have 3 tabs

        - the description of the lb scheme,
        - the properties of the lb scheme,
        - the equivalent equations of the lb scheme.

        """

        self.test_case = test_case
        self.known_cases = known_cases
        self.default_cases = {
            c.name: c for c in known_cases[test_case.get_case()]
        }
        self.cases = {
            c.name: copy.copy(c) for c in known_cases[test_case.get_case()]
        }
        self.parameters = {}

        ##
        ## The menu
        ##
        default_case = list(self.cases.keys())[0]
        self.select_case = v.Select(
            items=list(self.cases.keys()),
            v_model=default_case,
            label='LBM schemes'
        )
        self.panels = v.ExpansionPanels(
            v_model=None, children=[ParametersPanel('Show parameters')]
        )
        self.reset = v.Btn(children=['reset to default'], class_='d-none')
        self.menu = [self.select_case, self.panels, self.reset]

        ##
        ## The main
        ##
        self.description = Markdown()
        self.properties = v.Layout()
        self.eq_pde = v.Layout()

        self.tabs = v.Tabs(
            v_model=0,
            children=
            [
                v.Tab(children=['Description']),
                v.Tab(children=['Properties']),
                v.Tab(children=['Equivalent equations']),
                v.TabItem(children=[self.description]),
                v.TabItem(children=[self.properties]),
                v.TabItem(children=[self.eq_pde]),
            ]
        )
        self.main = [self.tabs]

        # populate the parameters and the description of the selected
        # lb scheme
        self.change_case(None)

        ##
        ## Widget events
        ##
        self.select_case.observe(self.change_case, 'v_model')

        # Allow to go back to the default parameters
        self.reset.on_event('click', self.reset_btn)

        # Check the tab id to activate the computation
        # of the equivalent equations or the scheme properties
        # since it can take time.
        self.tabs.observe(self.change_tab, 'v_model')

        # If the test case is changed, we need to list the available
        # lb schemes for this test.
        self.test_case.select_case.observe(self.change_test_case, 'v_model')

        # Bind each parameter to change_param
        # to make the reset button available if needed.
        self.panels.children[0].bind(self.change_param)

    def change_param(self, change):
        self.reset.class_ = ''

    def change_tab(self, change):
        """
        Check the tab id.

        if 1, compute the properties of the scheme
        if 2, compute the equivalent equations
        """
        case = self.cases[self.select_case.v_model]
        if self.tabs.v_model == 1 and not self.properties.children:
            self.properties.children = [
                Message('Compute the properties of the scheme')
            ]
            self.properties.children = [case.get_information().vue()]
        if self.tabs.v_model == 2 and not self.eq_pde.children:
            self.eq_pde.children = [
                Message('Compute the equivalent equations of the scheme')
            ]
            self.eq_pde.children = [case.get_eqpde().vue()]

    def change_test_case(self, change):
        """
        If the test case is changed, 
        update the default_cases and cases dictionary,
        update the selection widget and update the list of parameters.
        """
        current_case = self.select_case.v_model
        test_case = self.test_case.get_case()
        self.default_cases = {c.name: c for c in self.known_cases[test_case]}
        self.cases = {c.name: c for c in self.known_cases[test_case]}

        # if the current lb scheme is in the list take it,
        # otherwise keep the first in the new selection list.
        if current_case not in self.cases.keys():
            current_case = list(self.cases.keys())[0]

        self.select_case.items = list(self.cases.keys())
        self.select_case.v_model = current_case

        # update the parameters list of the selected lb scheme.
        self.change_case(None)

    def change_case(self, change):
        v_model = self.tabs.v_model
        case = self.cases[self.select_case.v_model]
        # test_case = self.test_case.get_case()
        self.parameters = schema_to_widgets(self.parameters, case)
        self.description.update_content(case.description)
        self.properties.children = []
        self.eq_pde.children = []
        self.panels.children[0].update(self.parameters.values())
        self.panels.children[0].bind(self.change_param)
        self.tabs.v_model = v_model

        if self.tabs.v_model > 0:
            self.change_tab(None)

        self.change_param(None)
        self.reset.class_ = 'd-none'

    def reset_btn(self, widget, event, data):
        """
        When the reset button is clicked, the current scheme is
        replaced by the origin lb scheme to recover the default
        parameters.
        """
        case = self.select_case.v_model
        self.cases[case] = copy.deepcopy(self.default_cases[case])
        self.change_case(None)
        self.select_case.notify_change({'name': 'v_model', 'type': 'change'})

    def get_case(self):
        """
        Get the current scheme.
        """
        case = self.cases[self.select_case.v_model]

        # update the parameters of the scheme with
        # those defined in the menu.
        for k, v in self.parameters.items():
            attr = getattr(case, k)
            if hasattr(attr, 'value'):
                attr.value = v.value
            else:
                attr = v.value
        return case
