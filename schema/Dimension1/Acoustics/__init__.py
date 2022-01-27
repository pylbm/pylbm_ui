# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#
# License: BSD 3 clause

# model
from .equation_type import EntropyAcoustics
# test cases
from .tc_bump import tc_bumpy_acc
from .tc_wave import tc_wave_acc
# schemes
from .D1q22 import D1Q22

cases = {
    'model': EntropyAcoustics,
    'default case': 'Bump_acoustics',
    'test cases': {
        'Bump_acoustics': {
            'test case': tc_bumpy_acc,
            'schemes': [
                D1Q22(la=2, s_rho=1.9, s_q=1.9),
            ]
        },
        'Wave_acoustics': {
            'test case': tc_wave_acc,
            'schemes': [
                D1Q22(la=2, s_rho=1.9, s_q=1.9),
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
