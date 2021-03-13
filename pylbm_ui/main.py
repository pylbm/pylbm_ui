import os
import sys

import ipyvuetify as v
from .tab_widgets import *

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

    tc = Test_case_widget(cases, default_case)
    lb = LB_scheme_widget(tc, known_cases)
    # lb = LB_scheme_widget(schemeDic, default_scheme, known_cases)

    tab_contents = {'Test case': tc.widget,
                    'Scheme': lb.widget,
                    'Linear stability': stability_widget(tc, lb).widget,
                    'LBM Simulation': simulation_widget(tc, lb).widget,
                    'Parametric study': parametric_widget(tc, lb).widget,
    }

    tab_list = [v.Tab(children=[k]) for k in tab_contents.keys()]
    content_list = [v.TabItem(children=[widget]) for widget in tab_contents.values()]

    tab = v.Tabs(
        v_model=None,
        center_active=True,
        dark=True,
        fixed_tabs=True,
        slider_size=4,
        children=tab_list + content_list)

    return v.Container(children=[v.Row(children=[v.Img(src='https://pylbm.readthedocs.io/en/latest/_static/img/pylbm_with_text.svg', max_width=400)], align='center', justify='center', class_='ma-2'),
                          v.Row(children=[tab])
    ])
    # return tab
