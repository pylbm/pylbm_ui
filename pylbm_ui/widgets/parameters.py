# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v
from .debug import debug
from .pylbmwidget import HTML, ParametersPanel

@debug
class option:
    def __init__(self, widget, change):
        self.widget = widget
        self.change = change


@debug
class ParametersWidget:
    def __init__(self):
        """
        Widget definition for parameters.

        This widget is composed by a menu where you can the parameters of the notebook.

        """
        ##
        ## The menu
        ##
        self.menu = []

        ##
        ## The main
        ##

        self.list_options = {}

        self.modify_widget()

    def add_option(self, name, widget, change):
        self.list_options[name] = option(widget, change)
        self.modify_widget()

    def modify_widget(self):
        self.widget_tabs = v.Tabs(
            v_model=None,
            children=[
                v.Tab(children=['Tabs options']),
                v.TabItem(
                    children=[
                        m.widget for m in self.list_options.values()
                    ]
                ),
            ]
        )
        self.main = [self.widget_tabs]


        # self.opt_ps = option(
        #     v.Switch(
        #         label='View parametric study tab',
        #         v_model=False,
        #         append_icon='mdi-atom',
        #         color='success',
        #         hint="Click me to view the PARAMETRIC STUDY tab"
        #     ),

        # )
        # self.opt_debug = v.Switch(
        #     label='View debug tab',
        #     v_model=False,
        #     append_icon='mdi-atom',
        #     color='error',
        #     hint="Click me to view the DEBUG tab"
        # )
