import os
import sys

import ipyvuetify as v
from .tab_widgets import *

from schema.toro import Toro1_1D, Toro2_1D, Toro3_1D, Toro4_1D, Toro5_1D

cases = {'toro 1': Toro1_1D,
         'toro 2': Toro2_1D,
         'toro 3': Toro3_1D,
         'toro 4': Toro4_1D,
         'toro 5': Toro5_1D,
}
default_case = 'toro 1'

from schema.D1q222 import D1Q222
from schema.D1q333 import D1Q333
from schema .D1q3L2_0 import D1Q3L2
schemeDic = {'D1Q222': D1Q222(dx=1.,la=1, s_rho=1.,s_u=1., s_p=1.),
             'D1Q333': D1Q333(dx=1.,la=1, s_rho=1.,s_u=1., s_p=1., s_rhox=1., s_ux=1., s_px=1.),
             'D1Q3L2': D1Q3L2(dx=1.,la=1, s_rho=1.,s_u=1., s_p=1., alpha=1.)}
default_scheme = 'D1Q222'

def main():

    tc = test_case_widget(cases, default_case)
    lb = LB_scheme_widget(schemeDic, default_scheme)

    tab_contents = {'Test case': tc.widget,
                    'Scheme': lb.widget,
                    'Linear stability': stability_widget(tc, lb).widget,
                    'LBM Simulation': simulation_widget(tc, lb).widget,
                    # 'Parametric study': parametric_widget().widget,
    }

    tab_list = [v.Tab(children=[k]) for k in tab_contents.keys()]
    content_list = [v.TabItem(children=[widget]) for widget in tab_contents.values()]

    tab = v.Tabs(
        v_model=None,
        center_active=True,
        dark=True,
        fixed_tabs=True,
        children=tab_list + content_list)

    return tab
