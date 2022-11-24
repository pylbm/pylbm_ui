# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#
# License: BSD 3 clause

# model
from .equation_type import D1_acoustics
# test cases
from .tc_bump import D1_acoustics_tc_bumpy
from .tc_wave import D1_acoustics_tc_wave
# schemes
from .D1q22 import D1_acoustics_D1Q22
from .D1q3 import D1_acoustics_D1Q3
from .D1q33 import D1_acoustics_D1Q33

cases = {
    'model': D1_acoustics,
    'default case': D1_acoustics_tc_bumpy.name,
    'test cases': {
        D1_acoustics_tc_bumpy.name: {
            'test case': D1_acoustics_tc_bumpy,
            'schemes': [
                D1_acoustics_D1Q3(la=1.5, s=1.9),
                D1_acoustics_D1Q22(la=1.5, s_rho=1.9, s_q=1.9),
                D1_acoustics_D1Q33(
                    la=1.5,
                    s_rho=1.8, s_rhox=1., s_q=1.8, s_qx=1.,
                    alpha=.75, beta=.75
                ),
            ]
        },
        D1_acoustics_tc_wave.name: {
            'test case': D1_acoustics_tc_wave,
            'schemes': [
                D1_acoustics_D1Q3(la=1.5, s=1.9),
                D1_acoustics_D1Q22(la=1.5, s_rho=1.9, s_q=1.9),
                D1_acoustics_D1Q33(
                    la=1.5,
                    s_rho=1.8, s_rhox=1., s_q=1.8, s_qx=1.,
                    alpha=.75, beta=.75
                ),
            ]
        },
    }
}
