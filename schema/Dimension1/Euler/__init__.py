from .toro import Toro1_1D, Toro2_1D, Toro3_1D, Toro4_1D, Toro5_1D

from .D1q222 import D1Q222
from .D1q333 import D1Q333, D1Q333_NS
from .D1q3L2_0 import D1Q3L2

cases = {
    'Toro 1': Toro1_1D,
    'Toro 2': Toro2_1D,
    'Toro 3': Toro3_1D,
    'Toro 4': Toro4_1D,
    'Toro 5': Toro5_1D
}

known_cases = {
    Toro1_1D: [
        D1Q222(la=5, s_rho=1.9, s_u=1.8, s_p=2.),
        D1Q333(
            la=10,
            s_rho=1.9, s_u=1.9, s_p=1.9,
            s_rhox=1.75, s_ux=1.75, s_px=1.75
        ),
        D1Q333_NS(
            la=10,
            s_rho=1.5, s_u=1.5, s_p=1.5,
            s_rhox=1., s_ux=1., s_px=1.
        ),
        D1Q3L2(
            la=5,
            s_rho=1.5, s_u=1.5, s_p=1.5,
            alpha=0.01
        ),
    ],
    Toro2_1D: [
        D1Q222(la=4, s_rho=1.7, s_u=1.7, s_p=1.7),
        D1Q333(
            la=10,
            s_rho=1.95, s_u=1.95, s_p=1.95,
            s_rhox=1.75, s_ux=1.5, s_px=1.75
        ),
        D1Q333_NS(
            la=20,
            s_rho=1.6, s_u=1.6, s_p=1.6,
            s_rhox=1.6, s_ux=1.6, s_px=1.6
        ),
        D1Q3L2(
            la=4,
            s_rho=1.7, s_u=1.7, s_p=1.7,
            alpha=0.01
        ),
    ],
    Toro3_1D: [
        D1Q222(la=60, s_rho=1.5, s_u=1.5, s_p=1.5),
        D1Q333(
            la=250,
            s_rho=1.9, s_u=1.9, s_p=1.9,
            s_rhox=1.5, s_ux=1.5, s_px=1.5
        ),
        D1Q333_NS(
            la=250,
            s_rho=1.6, s_u=1.6, s_p=1.6,
            s_rhox=1., s_ux=1., s_px=1.
        ),
        D1Q3L2(
            la=175,
            s_rho=1.6, s_u=1.6, s_p=1.6,
            alpha=0.01
        ),
    ],
    Toro4_1D: [
        D1Q222(la=50, s_rho=1.8, s_u=1.8, s_p=1.8),
        D1Q333(
            la=100,
            s_rho=1.8, s_u=1.8, s_p=1.8,
            s_rhox=1.5, s_ux=1.5, s_px=1.5
        ),
        D1Q333_NS(
            la=100,
            s_rho=1.6, s_u=1.6, s_p=1.6,
            s_rhox=1., s_ux=1., s_px=1.
        ),
        D1Q3L2(
            la=100,
            s_rho=1.8, s_u=1.8, s_p=1.8,
            alpha=0.01
        ),
    ],
    Toro5_1D: [
        D1Q222(la=40, s_rho=1.85, s_u=1.8, s_p=1.6),
        D1Q333(
            la=100,
            s_rho=1.9, s_u=1.8, s_p=1.8,
            s_rhox=1.8, s_ux=1.8, s_px=1.8
        ),
        D1Q333_NS(
            la=100,
            s_rho=1.5, s_u=1.5, s_p=1.5,
            s_rhox=1., s_ux=1., s_px=1.
        ),
        D1Q3L2(
            la=100,
            s_rho=1.5, s_u=1.5, s_p=1.5,
            alpha=0.01
        ),
    ],
}
