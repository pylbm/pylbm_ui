# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
from pydantic import BaseModel
import sympy as sp
import pylbm
from .equation_type import Euler1D
from ...utils import LBM_scheme, RelaxationParameter, RealParameter


class D1Q3L2(LBM_scheme):
    s_rho: RelaxationParameter('s_rho')
    s_u: RelaxationParameter('s_u')
    s_p: RelaxationParameter('s_p')
    alpha: RealParameter('alpha')
    # alpha: float
    equation = Euler1D()
    dim = 1
    name = 'D1Q3L2'
    tex_name = r'$D_1Q_3L_2$'

    def get_required_param(self):
        return [self.equation.gamma]

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        E = self.equation.E
        gamma = self.equation.gamma

        la_, la = self.la.symb, self.la.value
        s_rho_, s_rho = self.s_rho.symb, self.s_rho.value
        s_u_, s_u = self.s_u.symb, self.s_u.value
        s_p_, s_p = self.s_p.symb, self.s_p.value

        sigma_1 = sp.symbols('sigma_1', constants=True)
        sigma_2 = sp.symbols('sigma_2', constants=True)
        sigma_3 = sp.symbols('sigma_3', constants=True)

        symb_s_1 = 1/(.5+sigma_1)          # symbolic relaxation parameter
        symb_s_2 = 1/(.5+sigma_2)          # symbolic relaxation parameter
        symb_s_3 = 1/(.5+sigma_3)          # symbolic relaxation parameter

        ALPHA_NORM, alpha = self.alpha.symb, self.alpha.value
        # ALPHA_NORM = sp.Symbol('alpha')
        # alpha = self.alpha
        ALPHA = ALPHA_NORM * la_**2

        la2 = la_**2
        u = q/rho
        EI = E - q**2/rho/2
        ee = (E/rho-u**2/2) / ALPHA  # p/rho / (gamma-1) / alpha
        p = (gamma-1) * EI

        v = [0, 1, 2, 0, 1, 2]              # velocities
        # self.nv = len(v)
        M = sp.Matrix(
            [
                [1, 1, 1, 1, 1, 1],
                [0, la_, -la_, 0, la_, -la_],
                [
                    0, la2/2, la2/2,
                    ALPHA, la2/2+ALPHA, la2/2+ALPHA
                ],
                [1, 1, 1, -1, -1, -1],
                [0, la_, -la_, 0, -la_, la_],
                [
                    0, la2/2, la2/2,
                    -ALPHA, -la2/2-ALPHA, -la2/2-ALPHA
                ],
            ]
        )
        deltarho = rho*(1-(3-gamma)*ee)
        deltaq = q * (1 + (la_**2-u**2)/ALPHA - 2*gamma*ee)
        # deltaEc = .25*(
        #     (q+deltaq)**2/(rho+deltarho)
        #     - (q-deltaq)**2/(rho-deltarho)
        # )
        # deltaE = deltaEc + p/(gamma-1) * (
        #     .5 - ee
        # )
        deltaE = E + p/(gamma-1) * (
            2 - (3-gamma)/2*u**2/ALPHA
        )

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': v,
                    'conserved_moments': [rho, q, E],
                    'M': M,
                    'relaxation_parameters': [
                        0, 0, 0,
                        symb_s_1, symb_s_2, symb_s_3
                    ],
                    'equilibrium': [
                        rho, q, E,
                        deltarho, deltaq, deltaE
                    ]
                },
            ],
            'parameters': {
                la_: la,
                ALPHA_NORM: alpha,
                s_rho_: s_rho,
                s_u_: s_u,
                s_p_: s_p,
                sigma_1: 1/s_rho_-.5,
                sigma_2: 1/s_u_-.5,
                sigma_3: 1/s_p_-.5,
            },
            'generator': 'numpy'
        }

    def get_boundary(self):
        return {
            self.equation.NonReflexiveOutlet: {
                'method': {
                    0: pylbm.bc.Neumann,
                },
            },
            self.equation.Neumann: {
                'method': {
                    0: pylbm.bc.Neumann,
                },
            },
            self.equation.Dirichlet_u: {
                'method': {
                    0: pylbm.bc.BounceBack,
                },
            },
        }
