# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#
# License: BSD 3 clause

# model
from .equation_type import Acoustics1D
# test cases
from .tc_bump import tc_bumpy_acc
from .tc_wave import tc_wave_acc
# schemes
from .D1q22 import D1Q22
from .D1q3 import D1Q3
from .D1q33 import D1Q33

cases = {
    'model': Acoustics1D,
    'default case': 'Bump_acoustics',
    'test cases': {
        'Bump_acoustics': {
            'test case': tc_bumpy_acc,
            'schemes': [
                D1Q3(la=2, s=1.9),
                D1Q22(la=1.5, s_rho=1.9, s_q=1.9),
                D1Q33(
                    la=1.5,
                    s_rho=1.8, s_rhox=1., s_q=1.8, s_qx=1.,
                    alpha=.75, beta=.75
                ),
            ]
        },
        'Wave_acoustics': {
            'test case': tc_wave_acc,
            'schemes': [
                D1Q3(la=2, s=1.9),
                D1Q22(la=1.5, s_rho=1.9, s_q=1.9),
                D1Q33(
                    la=1.5,
                    s_rho=1.8, s_rhox=1., s_q=1.8, s_qx=1.,
                    alpha=.75, beta=.75
                ),
            ]
        },
        # 'Indicator': {
        #     'test case': tc_indy,
        #     'schemes': [
        #         D1Q2(la=2, s_u=1.9),
        #     ]
        # }
    }
}
