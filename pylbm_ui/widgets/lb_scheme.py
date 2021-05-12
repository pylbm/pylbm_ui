# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v

from ..utils import schema_to_widgets
from .debug import debug
from .pylbmwidget import Markdown, ParametersPanel
from .message import Message


@debug
class LBSchemeWidget:
    def __init__(self, test_case):
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
        self.parameters = {}

        ##
        ## The menu
        ##
        # default_case = next(iter(self.cases.keys()))
        self.select_case = v.Select(
            items=[],
            v_model=None,
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
            children=[
                v.Tab(children=['Description']),
                v.Tab(children=['Properties']),
                v.Tab(children=['Equivalent equations']),
                v.TabItem(children=[self.description]),
                v.TabItem(children=[self.properties]),
                v.TabItem(children=[self.eq_pde]),
            ]
        )
        self.main = [self.tabs]

        # populate the schemes of the selected test case
        self.change_test_case(None)
        # populate the parameters and the description of
        # the selected lb scheme
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

    def fix_selected_cases(self):
        self.selected_schemes_names = [
            scheme.name for scheme in self.test_case.get_schemes()
        ]
        self.selected_schemes_indices = {
            nk: k for k, nk in enumerate(self.selected_schemes_names)
        }

    def change_test_case(self, change):
        """
        If the test case is changed, 
        update the default_cases and cases dictionary,
        update the selection widget and update the list of parameters.
        """
        current_case = self.select_case.v_model
        self.fix_selected_cases()

        # if the current lb scheme is in the list take it,
        # otherwise keep the first in the new selection list.
        if current_case not in self.selected_schemes_names:
            current_case = self.selected_schemes_names[0]

        self.select_case.items = self.selected_schemes_names
        self.select_case.v_model = current_case

        # update the parameters list of the selected lb scheme.
        self.change_case(None)

    def get_case(self):
        return self.test_case.get_schemes()[
            self.selected_schemes_indices[self.select_case.v_model]
        ]

    def parameters_widget2scheme(self):
        """
        update the parameters of the scheme with
        those defined in the menu
        """
        case = self.get_case()
        for k, v in self.parameters.items():
            attr = getattr(case, k)
            if hasattr(attr, 'value'):
                attr.value = v.value
            else:
                attr = v.value

    def change_case(self, change):
        v_model = self.tabs.v_model
        case = self.get_case()
        self.parameters = schema_to_widgets(self.parameters, case)
        self.description.update_content(case.description)
        self.properties.children = []
        self.eq_pde.children = []
        self.panels.children[0].update(self.parameters.values())
        self.panels.children[0].bind(self.change_param)
        self.tabs.v_model = v_model

        if self.tabs.v_model > 0:
            self.change_tab(None)

        self.reset.class_ = 'd-none'

    def change_param(self, change):
        """
        Check if the parameters are changed from the default
        and show the reset button if yes.
        Plot the reference solution if it exists.
        """
        case = self.get_case()
        default_values = case.default_values

        # check if the parameters of the current case are the
        # same of the default one.
        is_same = True
        for k, v in self.parameters.items():
            attr = default_values.get(k, None)
            if v.value != attr:
                is_same = False

        # if the parameters are different from the default one
        # we show the reset button
        if not is_same:
            self.reset.class_ = ''
            self.parameters_widget2scheme()
        else:
            self.reset.class_ = 'd-none'
        # update the tab
        self.change_tab(None)

    def change_tab(self, change):
        """
        Check the tab id.

        if 1, compute the properties of the scheme
        if 2, compute the equivalent equations
        """
        case = self.get_case()
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

    def reset_btn(self, widget, event, data):
        """
        When the reset button is clicked, the current scheme is
        replaced by the origin lb scheme to recover the default
        parameters.
        """
        case = self.get_case()
        # update the parameters of the scheme with
        # those defined in default_values variable
        for k, v in self.parameters.items():
            v.v_model = case.default_values.get(k, None)

        self.parameters_widget2scheme()
        self.select_case.notify_change({'name': 'v_model', 'type': 'change'})
