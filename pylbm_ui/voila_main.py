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

from schema import cases  # , default_case, known_cases


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

    resume = v.Html(
        tag='div', class_='d-flax flex-column',
        children=[],
        nav=True,
        v_model='drawer',
    )

    def tab_change(change):
        tab_id = tab.v_model
        widget = tab_widgets[tab_id]
        menu.children = [
            v.ListItem(
                children=[
                    v.ListItemContent(children=[m])
                ]
            ) for m in widget.menu
        ]
        content.children = widget.main

        res_child = []
        if tab_id < 6:
            if tab_id >= 1:
                res_child.append(
                    v.Btn(
                        class_='ma-2 gray',
                        children=[
                            f"{mc.select_category.v_model}: " + 
                            f"{mc.select_model.v_model}"
                        ]
                    )
                )
            if tab_id >= 2:
                res_child.append(
                    v.Btn(
                        class_='ma-2 gray',
                        children=[f"Test case:{tc.select_case.v_model}"]
                    )
                )
            if tab_id >= 3:
                res_child.append(
                    v.Btn(
                        class_='ma-2 gray',
                        children=[f"Scheme: {lb.select_case.v_model}"]
                    )
                )
        resume.children = res_child
        if tab_id == 6:
            posttreatment.update(None)

    tab_change(None)
    tab.observe(tab_change, 'v_model')

    navicon = v.AppBarNavIcon()

    drawer = v.NavigationDrawer(
        children=[
            v.Row(
                children=[
                    v.Img(
                        # src='https://pylbm.readthedocs.io/en/latest/_static/img/pylbm_with_text.svg',
                        src='img/pylbm_with_text.svg',
                        max_width=250, class_='ma-5'
                    )
                ],
                align='center',
                justify='center'
            ),
            resume,
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
