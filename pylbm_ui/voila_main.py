# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import os
import sys

import ipyvuetify as v
from .widgets import *

from schema import cases

sorted_list_tabs = [
    'model', 'test case', 'scheme',
    'linear stability', 'simulation',
    'parametric study', 'post treatment',
    'configuration',
    'debug'
]


def change_list_tabs(link_widget_tab):
    """
    create the list of tabs

    Parameters
    ----------

    link_widget_tab: dict
        the dictionary (keys are title and value are tuple (widget, bool))

    Returns
    -------

    tab_widgets: list
        the list of the widget viewed in the tabs

    tab_titles: list
        the list of the titles viewed in the tabs

    tab_indices: dict
        the dictionary (keys are title and value are the index in the tab)    
    """
    tab_widgets, tab_titles = [], []
    tab_indices, index = {}, 0
    for title in sorted_list_tabs:
        widget, view = link_widget_tab.get(title, (None, False))
        if view:
            tab_widgets.append(widget)
            tab_titles.append(title)
            tab_indices[title] = index
            index += 1
    return tab_widgets, tab_titles, tab_indices


def get_information(tab_name, mc, tc, lb, param):
    """
    return the widget of informations if needed
    according to the tab_name
    """

    # nothing for the model
    if tab_name == 'debug':
        return []

    # nothing for the model
    if tab_name == 'model':
        return []

    # nothing for the post treatment
    if tab_name == 'post treatment':
        return []

    # visualization of the options for the configuration
    if tab_name == 'configuration':
        lst_print = []
        for name, option in param.list_options.items():
            lst_print.append(
                f"{name}: {option.widget.v_model}\n"
            )
        return [
            v.Card(children=[
                v.CardTitle(children=['Informations'], class_='pb-1'),
                v.List(children=lst_print,
                dense=True,
                class_='pa-0')
            ])
        ]

    # for test case, scheme, ...
    items = [
        v.ListItem(children=[
            v.ListItemContent(children=[
                f"{mc.select_category.v_model}: " + f"{mc.select_model.v_model}"
            ],
            class_='px-4 py-0'
            )
        ],
        class_='mb-0'),
        v.ListItem(children=[
            v.ListItemContent(children=[
                f"Test case: {tc.select_case.v_model}"
            ],
            class_='px-4 py-0',
            )
        ],
        class_='mb-0'),
        v.ListItem(children=[
            v.ListItemContent(children=[
                f"Scheme: {lb.select_case.v_model}"
            ],
            class_='px-4 py-0',
            )
        ],
        class_='mb-0'),
    ]
    
    num = 0
    if tab_name == 'test case':
        num = 1
    if tab_name == 'scheme':
        num = 2
    if tab_name == 'linear stability':
        num = 3
    if tab_name == 'simulation':
        num = 3
    if tab_name == 'parametric study':
        num = 3

    return [
        v.Card(children=[
            v.CardTitle(children=['Informations'], class_='pb-1'),
            v.List(children=items[0:num],
            dense=True,
            class_='pa-0')
        ])
    ]

@debug_func
def main():

    param = ParametersWidget()
    mc = ModelWidget(cases)
    tc = TestCaseWidget(mc)
    lb = LBSchemeWidget(tc)

    stability =  StabilityWidget(tc, lb)
    simulation = SimulationWidget(tc, lb)
    parametric = ParametricStudyWidget(
        tc, lb, simulation.discret, simulation.codegen
    )
    posttreatment = PostTreatmentWidget()

    class DebugWidget:
        def __init__(self):
            self.menu = []
            self.main = [out]
    bugtab = DebugWidget()

    link_widget_tab = {
        'configuration': [param, True],
        'model': [mc, True],
        'test case': [tc, True],
        'scheme': [lb, True],
        'linear stability': [stability, True],
        'simulation': [simulation, True],
        'parametric study': [parametric, True],
        'post treatment': [posttreatment, True],
        'debug': [bugtab, True],
    }

    tab = v.Tabs(
        v_model=None,
        center_active=True,
        fixed_tabs=True,
        slider_size=4,
        align_with_title=True,
        show_arrows=True,
        children=[]
    )

    menu = v.List(
        children=[],
        nav=True,
        v_model='drawer',
    )
    content = v.Content(children=[])

    @debug_func
    def tab_change(change):
        """
        change the tab
        """
        # print(tab.v_model)
        tab_widgets, tab_titles, tab_indices = change_list_tabs(link_widget_tab)
        if tab.v_model is None:
            tab_name = 'configuration'
            tab_id = tab_indices.get(tab_name, 0)
        else:
            tab_id = tab.v_model
        tab_name = tab_titles[tab_id]
        # print(f"{tab_id}: {tab_name}")
        # print(tab_titles)

        items = get_information(tab_name, mc, tc, lb, param)

        widget = tab_widgets[tab_id]
        items.extend([
            v.ListItem(
                children=[
                    v.ListItemContent(children=[m])
                ]
            ) for m in widget.menu
        ])

        menu.children = items
        content.children = widget.main

        if tab_name == 'simulation':
            simulation.update_simu_cfg_list()

        if tab_name == 'parametric study':
            parametric.update_param_cfg_list()

        if tab_name == 'post treatment':
            posttreatment.update(None)

    @debug_func
    def list_tab_change(change):
        """
        change the list of tabs
        """
        # change the link_widget_tab dictionary
        link_widget_tab['parametric study'][1] = param.list_options['ps'].widget.v_model
        link_widget_tab['post treatment'][1] = param.list_options['pt'].widget.v_model
        link_widget_tab['debug'][1] = param.list_options['debug'].widget.v_model

        tab_id = tab.v_model  # id in the old tab
        if tab_id is not None:
            tab_name = tab.children[tab_id].children[0]  # title
        else:
            tab_name = 'configuration'  # default title
        # compute the new tab (parameters can modify the list)
        _, tab_titles, tab_indices = change_list_tabs(link_widget_tab)
        # update the widget with the new list of tabs
        tab.children = [
           v.Tab(children=[k]) for k in tab_titles
        ]
        tab.v_model = tab_indices[tab_name]
        
    # TO MODIFY ICON:
    # https://materialdesignicons.com
    param.add_option(
        'ps',
        v.Switch(
            label='View parametric study tab',
            v_model=False,
            append_icon='mdi-eye-check-outline',
            color='success',
            hint="Click me to view the PARAMETRIC STUDY tab"
        ),
        list_tab_change
    )
    param.add_option(
        'pt',
        v.Switch(
            label='View post treatment tab',
            v_model=False,
            append_icon='mdi-eye-check-outline',
            color='success',
            hint="Click me to view the POST TREATMENT tab"
        ),
        list_tab_change
    )
    param.add_option(
        'debug',
        v.Switch(
            label='View debug tab',
            v_model=False,
            append_icon='mdi-atom',
            color='error',
            hint="Click me to view the DEBUG tab"
        ),
        list_tab_change
    )

    # tab_change(None)
    tab.observe(tab_change, 'v_model')
    mc.select_category.observe(tab_change, 'v_model')
    mc.select_model.observe(tab_change, 'v_model')
    tc.select_case.observe(tab_change, 'v_model')
    lb.select_case.observe(tab_change, 'v_model')
    for option in param.list_options.values():
        option.widget.observe(option.change, 'v_model')
    list_tab_change(None)
    
    navicon = v.AppBarNavIcon()

    drawer = v.NavigationDrawer(
        children=[
            v.Row(
                children=[
                    v.Img(
                        src='img/pylbm_with_text.svg',
                        max_width=250, class_='ma-5'
                    )
                ],
                align='center',
                justify='center'
            ),
            menu
        ],
        v_model=True,
        width=350,
        clipped=True,
        app=True
    )

    def show_drawer(widget, event, data):
        drawer.v_model = not drawer.v_model

    navicon.on_event("click.stop", show_drawer)

    return v.App(
        children=[
            v.AppBar(
                children=[
                    navicon,
                    tab,
                ],
                clipped_left=True,
                app=True,
                dark=True,
            ),
            drawer,
            content,
        ]
    )
