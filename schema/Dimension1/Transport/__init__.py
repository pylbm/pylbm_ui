from .tc_bump import Bump_discont, Bump_C0

from .D1q2 import D1Q2

cases = {
    'Bump_disc': Bump_discont,
    'Bump_C0': Bump_C0,
}

known_cases = {
    Bump_discont: [
        D1Q2(la=2, s_u=1.9),
    ],
    Bump_C0: [
        D1Q2(la=2, s_u=1.9),
    ],
}
