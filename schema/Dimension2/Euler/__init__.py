# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

# model
from .equation_type import Euler2D
# test cases
from .tc_2D_Wedge import Wedge_Ma2p5, Wedge_Ma8
from .tc_2D_Implosion import Implosion2D_Symmetric
from .tc_2D_FFS import FFS_Ma3
# schemes
from .D2q4444 import D2Q4444

# cases = {
#     'Wedge Ma2p5': Wedge_Ma2p5,
#     'Wedge Ma 8': Wedge_Ma8,
#     'Implosion': Implosion2D_Symmetric,
#     'Forward Facing Step': FFS_Ma3,
# }

# known_cases = {
#     Wedge_Ma2p5: [
#         D2Q4444(
#             la=15,
#             s_rho=1.7647, s_u=1.7647, s_p=1.7647,
#             s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
#         )
#     ],
#     Wedge_Ma8: [
#         D2Q4444(
#             la=40,
#             s_rho=1.7647, s_u=1.7647, s_p=1.7647,
#             s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
#         )
#     ],
#     Implosion2D_Symmetric: [
#         D2Q4444(
#             la=10,
#             s_rho=1.904, s_u=1.904, s_p=1.904,
#             s_rho2=1.904, s_u2=1.904, s_p2=1.904
#         )
#     ],
#     FFS_Ma3: [
#         D2Q4444(
#             la=15,
#             s_rho=1.7647, s_u=1.7647, s_p=1.7647,
#             s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
#         )
#     ],
# }

# default_case = 'Wedge Ma2p5'

cases = {
    'model': Euler2D,
    'test cases': {
        'default': 'Wedge Ma=2.5',
        'Wedge Ma=2.5': {
            'test case': Wedge_Ma2p5,
            'schemes': [
                D2Q4444(
                    la=15,
                    s_rho=1.7647, s_u=1.7647, s_p=1.7647,
                    s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
                )
            ]
        },
        'Wedge Ma=8': {
            'test case': Wedge_Ma8,
            'schemes': [
                D2Q4444(
                    la=40,
                    s_rho=1.7647, s_u=1.7647, s_p=1.7647,
                    s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
                )
            ]
        },
        'Implosion': {
            'test case': Implosion2D_Symmetric,
            'schemes': [
                D2Q4444(
                    la=10,
                    s_rho=1.904, s_u=1.904, s_p=1.904,
                    s_rho2=1.904, s_u2=1.904, s_p2=1.904
                )
            ]
        },
        'Forward Facing Step': {
            'test case': FFS_Ma3,
            'schemes':[
                D2Q4444(
                    la=15,
                    s_rho=1.7647, s_u=1.7647, s_p=1.7647,
                    s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
                )
            ]
        },
    }
}
