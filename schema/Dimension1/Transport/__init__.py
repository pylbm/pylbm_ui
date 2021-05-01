from .tc_bump import Bump_discont

from .D1q2 import D1Q2

cases = {
    'Bump_disc': Bump_discont,
}

known_cases = {
    Bump_discont: [
        D1Q2(la=2, s_u=1.9),
    ],
}
