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

from schema.toro import Toro1_1D, Toro2_1D, Toro3_1D, Toro4_1D, Toro5_1D
from schema.tc_2D_Wedge import Wedge_Ma2p5, Wedge_Ma8
from schema.tc_2D_Implosion import Implosion2D_Symmetric
from schema.tc_2D_FFS import FFS_Ma3

cases = {'Toro 1': Toro1_1D,
         'Toro 2': Toro2_1D,
         'Toro 3': Toro3_1D,
         'Toro 4': Toro4_1D,
         'Toro 5': Toro5_1D,
         'Wedge Ma2p5': Wedge_Ma2p5,
         'Wedge Ma 8': Wedge_Ma8,
         'Implosion': Implosion2D_Symmetric,
         'Forward Facing Step': FFS_Ma3,
}
default_case = 'Toro 1'

from schema.D1q222 import D1Q222
from schema.D1q333 import D1Q333
from schema.D1q3L2_0 import D1Q3L2
from schema.D2q4444 import D2Q4444

known_cases = {
    Toro1_1D: [
        D1Q222(la=5, s_rho=1.9,s_u=1.8, s_p=2.),
        D1Q333(la=10, s_rho=1.9, s_u=1.9, s_p=1.9, s_rhox=1.75, s_ux=1.75, s_px=1.75),
        D1Q3L2(la=5, s_rho=1.5, s_u=1.5, s_p=1.5, alpha=0.125),
    ],
    Toro2_1D: [
        D1Q222(la=4, s_rho=1.7, s_u=1.7, s_p=1.7),
        D1Q333(la=10, s_rho=1.95, s_u=1.95, s_p=1.95, s_rhox=1.75, s_ux=1.5, s_px=1.75),
        D1Q3L2(la=4, s_rho=1.7, s_u=1.7, s_p=1.7, alpha=0.125),
    ],
    Toro3_1D: [
        D1Q222(la=60, s_rho=1.5, s_u=1.5, s_p=1.5),
        D1Q333(la=250, s_rho=1.9, s_u=1.9, s_p=1.9, s_rhox=1.5, s_ux=1.5, s_px=1.5),
        D1Q3L2(la=60, s_rho=1.5, s_u=1.5, s_p=1.5, alpha=0.125),
    ],
    Toro4_1D: [
        D1Q222(la=50, s_rho=1.8, s_u=1.8, s_p=1.8),
        D1Q333(la=100, s_rho=1.8, s_u=1.8, s_p=1.8, s_rhox=1.5, s_ux=1.5, s_px=1.5),
        D1Q3L2(la=50, s_rho=1.8, s_u=1.8, s_p=1.8, alpha=0.125),
    ],
    Toro5_1D: [
        D1Q222(la=40, s_rho=1.85, s_u=1.8, s_p=1.6),
        D1Q333(la=100, s_rho=1.9, s_u=1.8, s_p=1.8, s_rhox=1.8, s_ux=1.8, s_px=1.8),
        D1Q3L2(la=40, s_rho=1.85, s_u=1.8, s_p=1.6, alpha=0.125),
    ],
    Wedge_Ma2p5: [
        D2Q4444(la=15, s_rho=1.7647, s_u=1.7647, s_p=1.7647, s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647)
    ],
    Wedge_Ma8: [
        D2Q4444(la=40, s_rho=1.7647, s_u=1.7647, s_p=1.7647, s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647)
    ],
    Implosion2D_Symmetric: [
        D2Q4444(la=10, s_rho=1.904, s_u=1.904, s_p=1.904, s_rho2=1.904, s_u2=1.904, s_p2=1.904)
    ],
    FFS_Ma3: [
        D2Q4444(la=15, s_rho=1.7647, s_u=1.7647, s_p=1.7647, s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647)
    ],
}

def main():

    tc = TestCaseWidget(cases, default_case)
    lb = LBSchemeWidget(tc, known_cases)

    stability =  StabilityWidget(tc, lb)
    simulation = simulation_widget(tc, lb)
    parametric = parametric_widget(tc, lb)
    posttreatment = PostTreatmentWidget()

    class DebugWidget:
        def __init__(self):
            self.menu = []
            self.main = [out]

    tab_widgets = [tc, lb, stability, simulation, parametric, posttreatment, DebugWidget()]
    tab_titles = ['Test case', 'Scheme', 'Linear stability', 'LBM Simulation', 'Parametric study', 'Post treatment', 'Debug']

    tab = v.Tabs(
        v_model=0,
        center_active=True,
        fixed_tabs=True,
        slider_size=4,
        align_with_title=True,
        show_arrows=True,
        children=[v.Tab(children=[k]) for k in tab_titles],
    )

    menu = v.List(children=[],
        nav=True,
        v_model='drawer',
    )
    content = v.Content(children=[])

    def tab_change(change):
        tab_id = tab.v_model
        widget = tab_widgets[tab_id]
        menu.children = [v.ListItem(children=[
                                       v.ListItemContent(children=[m])]) for m in widget.menu
        ]
        content.children = widget.main

        if tab_id == 5:
            posttreatment.update(None)


    tab_change(None)
    tab.observe(tab_change, 'v_model')

    navicon = v.AppBarNavIcon()

    drawer = v.NavigationDrawer(children=[
        v.Row(children=[
            v.Img(src='https://pylbm.readthedocs.io/en/latest/_static/img/pylbm_with_text.svg', max_width=250, class_='ma-5')],
                  align='center',
                  justify='center'),
            menu],
            v_model=True,
            width=350,
            clipped=True,
            app=True
    )

    def show_drawer(widget, event, data):
        drawer.v_model = not drawer.v_model

    navicon.on_event("click.stop", show_drawer)

    return v.App(children=[
                v.AppBar(children=[
                    navicon,
                    tab,
                ],
                clipped_left=True,
                app=True,
                dark=True,
                ),
        drawer,
        content,
    ])