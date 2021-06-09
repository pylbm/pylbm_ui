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

@debug_func
def get_information(tab_id, mc, tc, lb):
    if tab_id == 0:
        return []

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

    return [
        v.Card(children=[
            v.CardTitle(children=['Information'], class_='pb-1'),
            v.List(children=items[0:min(tab_id, 3)],
            dense=True,
            class_='pa-0')
        ])
    ]

@debug_func
def main():

    mc = ModelWidget(cases)
    tc = TestCaseWidget(mc)
    lb = LBSchemeWidget(tc)

    stability =  StabilityWidget(tc, lb)
    simulation = SimulationWidget(tc, lb)
    parametric = ParametricStudyWidget(tc, lb, simulation.discret)
    posttreatment = PostTreatmentWidget()

    class DebugWidget:
        def __init__(self):
            self.menu = []
            self.main = [out]

    tab_widgets = [
        mc,
        tc, lb,
        stability, simulation,
        parametric, posttreatment,
        DebugWidget()
    ]
    tab_titles = [
        'Model',
        'Test case', 'Scheme',
        'Linear stability', 'LBM Simulation',
        'Parametric study', 'Post treatment',
        'Debug'
    ]

    tab = v.Tabs(
        v_model=0,
        center_active=True,
        fixed_tabs=True,
        slider_size=4,
        align_with_title=True,
        show_arrows=True,
        children=[v.Tab(children=[k]) for k in tab_titles],
    )

    menu = v.List(
        children=[],
        nav=True,
        v_model='drawer',
    )
    content = v.Content(children=[])

    def tab_change(change):
        tab_id = tab.v_model

        items = []
        if tab_id < 6:
            items.extend(get_information(tab_id, mc, tc, lb))

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

        if tab_id == 4:
            simulation.update_simu_cfg_list()

        if tab_id == 5:
            parametric.update_param_cfg_list()

        if tab_id == 6:
            posttreatment.update(None)

    tab_change(None)
    tab.observe(tab_change, 'v_model')
    mc.select_category.observe(tab_change, 'v_model')
    mc.select_model.observe(tab_change, 'v_model')
    tc.select_case.observe(tab_change, 'v_model')
    lb.select_case.observe(tab_change, 'v_model')

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
