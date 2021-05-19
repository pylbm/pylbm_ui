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
        default_category = next(iter(self.cases))

        ##
        ## The menu
        ##

        # widget to select the model
        self.select_category = v.Select(
            items=list(self.cases.keys()),
            v_model=default_category,
            label='Category',
        )
        self.select_model = v.Select(
            items=[],
            v_model=None,
            label='Model'
        )
        self.menu = [self.select_category, self.select_model]

        ##
        ## The main
        ##

        self.description = Markdown()

        self.tabs = v.Tabs(
            v_model=None,
            children=[
                v.Tab(children=['Description']),
                v.TabItem(children=[self.description]),
            ]
        )

        self.main = [self.tabs]

        # Add the widget events
        self.select_category.observe(self.change_category, 'v_model')
        self.select_model.observe(self.change_model, 'v_model')

        # update the category to fix the default model
        self.change_category(None)

    def get_category(self):
        """Return the current category"""
        return self.select_category.v_model

    def change_category(self, change):
        """
        When the category is changed, 
        we have to update the list of models.
        """
        self.select_model.items = list(
            self.cases[self.get_category()].keys()
        )
        self.select_model.v_model = self.select_model.items[0]

    def get_model(self):
        """Return the current model."""
        return self.cases[self.get_category()][self.select_model.v_model]

    def change_model(self, change):
        """
        when the model is changed,
        we have to update the description of the model.
        """
        model = self.get_model()['model']()
        self.description.update_content(model.description)
