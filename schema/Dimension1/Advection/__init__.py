# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

# model
from .equation_type import Transport1D
# test cases
from .tc_bump import Bump_discont, Bump_C0
# schemes
from .D1q2 import D1Q2

# cases = {
#     'Bump_disc': Bump_discont,
#     'Bump_C0': Bump_C0,
# }

# known_cases = {
#     Bump_discont: [
#         D1Q2(la=2, s_u=1.9),
#     ],
#     Bump_C0: [
#         D1Q2(la=2, s_u=1.9),
#     ],
# }

# default_case = 'Bum_C0'

cases = {
    'model': Transport1D,
    'test cases': {
        'default': 'Bump_C0',
        'Bump_disc': {
            'test case': Bump_discont,
            'schemes': [
                D1Q2(la=2, s_u=1.9),
            ]
        },
        'Bump_C0': {
            'test case': Bump_C0,
            'schemes': [
                D1Q2(la=2, s_u=1.9),
            ]
        },
    }
}
