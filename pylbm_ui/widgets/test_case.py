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
from .debug import debug
from .pylbmwidget import Markdown, ParametersPanel, out


@debug
class TestCaseWidget:
    def __init__(self, model):
        """
        Widget definition for test cases.

        Parameters
        ==========

        - cases: dict
            the keys of this dictionary are the name of the test case,
            the values  of this dictionary are an instance of the test case.

        - default_case: str
            one of the keys found into the dictionary cases.

        This widget is composed by a menu where you can choose the test case and
        modify its default parameters. If you change any of the parameters, you will
        see a reset button to revover the default parameters of this case.

        This widget is also composed by a main widget where a description of the test cases
        is given and a plot of the reference solution if it exists.

        """
        self.model = model
        self.default_cases = model.cases
        # make a copy to not modify the input instances
        self.cases = copy.deepcopy(model.cases)
        self.parameters = {}

        ##
        ## The menu
        ##

        # widget to select the test case
        # liste_cases = list(self.cases.keys())
        liste_cases = list(
            self.model.get_model()['test cases'].keys()
        )
        default_case = self.model.get_model().get(
            'default case', liste_cases[0]
        )
        self.select_case = v.Select(
            items=liste_cases,
            v_model=default_case,
            label='Test cases'
        )
        self.panels = v.ExpansionPanels(
            v_model=None,
            children=[ParametersPanel('Show parameters')]
        )
        self.reset = v.Btn(children=['reset to default'], class_='d-none')
        self.menu = [self.select_case, self.panels, self.reset]

        ##
        ## The main
        ##
        self.description = Markdown()

        plt.ioff()
        self.fig = plt.figure(figsize=(12, 6))
        self.fig.canvas.header_visible = False

        self.tabs = v.Tabs(
            v_model=None,
            children=[
                v.Tab(children=['Description']),
                v.Tab(children=['Reference results']),
                v.TabItem(children=[self.description]),
                v.TabItem(children=[self.fig.canvas]),
            ]
        )

        self.main = [self.tabs]

        # Observe the change of model
        self.model.select_dim.observe(self.change_model, 'v_model')
        self.model.select_model.observe(self.change_model, 'v_model')

        # Add the widget events
        self.reset.on_event('click', self.reset_btn)
        self.select_case.observe(self.change_case, 'v_model')
        self.panels.children[0].bind(self.change_param)
        self.change_case(None)

    def reset_btn(self, widget, event, data):
        """
        When the reset button is clicked, the current test case is
        replaced by the origin test case to recover the default
        parameters.
        """
        self.set_case(self.get_default_case())
        self.change_case(None)

    def change_param(self, change):
        """
        Check if the parameters are changed from the default
        and show the reset button if yes.
        Plot the reference solution if it exists.
        """
        case = self.get_case()
        default_case = self.get_default_case()

        # check if the parameters of the current case are the
        # same of the default one.
        is_same = True
        for k, v in self.parameters.items():
            setattr(case, k, v.value)
            attr = getattr(default_case, k)
            if v.value != attr:
                is_same = False

        # if the parameters are different from the default one
        # we show the reset button
        if not is_same:
            self.reset.class_ = ''
        else:
            self.reset.class_ = 'd-none'

        # if the test case has a plot_ref_solution method
        # call it to plot the exact solution
        if hasattr(case, 'plot_ref_solution'):
            for axe in self.fig.axes:
                self.fig.delaxes(axe)
            case.plot_ref_solution(self.fig)
            self.fig.canvas.draw_idle()
            self.tabs.children[1].disabled = False
        else:
            # disable the tab 'reference results'
            self.tabs.children[1].disabled = True
            self.tabs.v_model = 0

    def change_case(self, change):
        """
        When the test case is changed, we have to update the description
        of the test case, make a new parameter lists in the menu.
        """
        case = self.get_case()
        self.panels.children[0].unbind(self.change_param)
        itab = self.tabs.v_model
        ipanel = self.panels.v_model
        self.description.update_content(
            case.description
        )
        self.parameters = schema_to_widgets(
            self.parameters,
            case
        )
        self.panels.children[0].update(self.parameters.values())
        self.panels.children[0].bind(self.change_param)
        self.tabs.v_model = itab
        self.panels.v_model = ipanel

        self.change_param(None)

    def get_case(self):
        """
        Return the current case.
        """
        model = self.cases[
            self.model.get_dim()
        ][self.model.select_model.v_model]
        return model['test cases'][self.select_case.v_model]['test case']

    def get_default_case(self):
        """
        Return the current case.
        """
        model = self.model.get_model()
        return model['test cases'][self.select_case.v_model]['test case']

    def set_case(self, icase):
        """set the current case to icase"""
        case = self.cases[
            self.model.get_dim()
        ][self.model.select_model.v_model]['test cases'][
            self.select_case.v_model
        ]
        case['test case'] = icase

    def change_model(self, change):
        """
        if the model is changed, update the test_cases
        """
        liste_cases = list(
            self.model.get_model()['test cases'].keys()
        )
        print(liste_cases)
        default_case = self.model.get_model().get(
            'default case', liste_cases[0]
        )
        self.select_case.items = liste_cases
        self.select_case.v_model = default_case
        # update the case
        self.change_case(None)
