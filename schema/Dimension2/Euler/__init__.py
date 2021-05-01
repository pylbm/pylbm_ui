from .tc_2D_Wedge import Wedge_Ma2p5, Wedge_Ma8
from .tc_2D_Implosion import Implosion2D_Symmetric
from .tc_2D_FFS import FFS_Ma3

from .D2q4444 import D2Q4444

cases = {
    'Wedge Ma2p5': Wedge_Ma2p5,
    'Wedge Ma 8': Wedge_Ma8,
    'Implosion': Implosion2D_Symmetric,
    'Forward Facing Step': FFS_Ma3,
}

known_cases = {
    Wedge_Ma2p5: [
        D2Q4444(
            la=15,
            s_rho=1.7647, s_u=1.7647, s_p=1.7647,
            s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
        )
    ],
    Wedge_Ma8: [
        D2Q4444(
            la=40,
            s_rho=1.7647, s_u=1.7647, s_p=1.7647,
            s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
        )
    ],
    Implosion2D_Symmetric: [
        D2Q4444(
            la=10,
            s_rho=1.904, s_u=1.904, s_p=1.904,
            s_rho2=1.904, s_u2=1.904, s_p2=1.904
        )
    ],
    FFS_Ma3: [
        D2Q4444(
            la=15,
            s_rho=1.7647, s_u=1.7647, s_p=1.7647,
            s_rho2=1.7647, s_u2=1.7647, s_p2=1.7647
        )
    ],
}