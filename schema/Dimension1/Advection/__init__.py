# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

# model
from .equation_type import Transport1D
# test cases
from .tc_bump import tc_bumpy
from .tc_indicator import tc_indy
# schemes
from .D1q2 import D1Q2
from .D1q3 import D1Q3

cases = {
    'model': Transport1D,
    'default case': 'Bump',
    'test cases': {
        'Bump': {
            'test case': tc_bumpy,
            'schemes': [
                D1Q2(la=2, s_u=1.9),
                D1Q3(la=2, s_u=1.9, s_ux=1.9, temperature=.5),
            ]
        },
        'Indicator': {
            'test case': tc_indy,
            'schemes': [
                D1Q2(la=2, s_u=1.9),
                D1Q3(la=2, s_u=1.9, s_ux=1.9, temperature=.5),
            ]
        }
    }
}
