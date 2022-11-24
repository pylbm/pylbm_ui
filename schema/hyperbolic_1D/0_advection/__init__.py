# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

# model
from .equation_type import D1_advection
# test cases
from .tc_bump import D1_advection_tc_bumpy
from .tc_indicator import D1_advection_tc_indy
# schemes
from .D1q2 import D1_advection_D1Q2
from .D1q3 import D1_advection_D1Q3

cases = {
    'model': D1_advection,
    'default case': D1_advection_tc_bumpy.name,
    'test cases': {
        D1_advection_tc_bumpy.name: {
            'test case': D1_advection_tc_bumpy,
            'schemes': [
                D1_advection_D1Q2(la=2, s_u=2),
                D1_advection_D1Q3(la=3, s_u=2, s_ux=2, temperature=.5),
            ]
        },
        D1_advection_tc_indy.name: {
            'test case': D1_advection_tc_indy,
            'schemes': [
                D1_advection_D1Q2(la=2, s_u=1.9),
                D1_advection_D1Q3(la=2, s_u=1.9, s_ux=1.9, temperature=.5),
            ]
        }
    }
}
