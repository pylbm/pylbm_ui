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
from .pylbmwidget import Markdown, ParametersPanel


@debug
class ModelWidget:
    def __init__(self, cases):
        """
        Widget definition for models.

        Parameters
        ==========

        cases: dict
            the keys of this dictionary are the name of the model,
            the values of this dictionary are an instance of the model.

        This widget is composed by a menu where you can choose the dimension
        and the model.

        This widget is also composed by a main widget
        where a description of the model is given.

        """
        self.cases = cases
        default_dimension = next(iter(self.cases))
        default_model = next(iter(self.cases[default_dimension]))

        ##
        ## The menu
        ##

        # widget to select the model
        self.select_dim = v.Select(
            items=list(self.cases.keys()),
            v_model=default_dimension,
            label='Spatial dimension',
            # append_icon='mdi-numeric'
        )
        self.select_model = v.Select(
            items=list(self.cases[default_dimension].keys()),
            v_model=default_model,
            label='Model'
        )
        self.menu = [self.select_dim, self.select_model]

        ##
        ## The main
        ##

        # self.description = Markdown()

        # plt.ioff()
        # self.fig = plt.figure(figsize=(12,6))
        # self.fig.canvas.header_visible = False

        # tabs_content = [v.TabItem(children=[self.description]), v.TabItem(children=[self.fig.canvas])]
        # self.tabs = v.Tabs(
        #     v_model=None,
        #     children=[v.Tab(children=['Description']),
        #                 v.Tab(children=['Reference results'])]
        #                 + tabs_content
        # )

        # self.main = [self.tabs]
        self.main = []

        # Add the widget events
        self.select_dim.observe(self.change_dim, 'v_model')
        self.change_dim(None)

    def change_dim(self, change):
        """
        When the dimension is changed, we have to update the description
        of the model.
        """
        self.select_model.items = list(
            self.cases[self.select_dim.v_model].keys()
        )
        self.select_model.v_model = self.select_model.items[0]

    def get_dim(self):
        """Return the current dimension"""
        return self.select_dim.v_model

    def get_model(self):
        """Return the current model."""
        return self.cases[self.get_dim()][self.select_model.v_model]

