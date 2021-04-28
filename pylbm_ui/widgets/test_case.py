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

class TestCaseWidget:
    def __init__(self, cases, default_case):
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
        self.default_cases = cases
        # make a copy to not modify the input instances
        self.cases = copy.deepcopy(cases)
        self.parameters = {}

        ##
        ## The menu
        ##

        # widget to select the test case
        self.select_case = v.Select(items=list(self.cases.keys()), v_model=default_case, label='Test cases')
        self.panels = v.ExpansionPanels(v_model=None, children=[ParametersPanel('Show parameters')])
        self.reset = v.Btn(children=['reset to default'], class_='d-none')
        self.menu = [self.select_case, self.panels, self.reset]

        ##
        ## The main
        ##
        self.description = Markdown()

        plt.ioff()
        self.fig = plt.figure(figsize=(12,6))
        self.fig.canvas.header_visible = False

        tabs_content = [v.TabItem(children=[self.description]), v.TabItem(children=[self.fig.canvas])]
        self.tabs = v.Tabs(
            v_model=None,
            children=[v.Tab(children=['Description']),
                        v.Tab(children=['Reference results'])]
                        + tabs_content
        )

        self.main = [self.tabs]

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
        case = self.select_case.v_model
        self.cases[case] = copy.deepcopy(self.default_cases[case])
        self.change_case(None)

    def change_param(self, change):
        """
        Check if the parameters are changed from the default
        and show the reset button if yes.
        Plot the reference solution if it exists.
        """
        icase = self.select_case.v_model
        case = self.cases[icase]
        default_case = self.default_cases[icase]

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
        with out:
            self.panels.children[0].unbind(self.change_param)
            itab = self.tabs.v_model
            ipanel = self.panels.v_model
            self.description.update_content(self.cases[self.select_case.v_model].description)
            self.parameters = schema_to_widgets(self.parameters, self.cases[self.select_case.v_model])
            self.panels.children[0].update(self.parameters.values())
            self.panels.children[0].bind(self.change_param)
            self.tabs.v_model = itab
            self.panels.v_model = ipanel

            self.change_param(None)

    def get_case(self):
        """
        Return the current case.
        """
        return self.cases[self.select_case.v_model]

