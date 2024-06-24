# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
# from pydantic import BaseModel, Field
import sympy as sp
import pylbm
import traitlets
from .equation_type import D1_advacoustics
from ...utils import LBM_scheme, RealParameter, RelaxationParameter


class D1_advacoustics_D1Q33(LBM_scheme):
    s_rho: RelaxationParameter('s_rho')
    s_q: RelaxationParameter('s_q')
    s_rhox: RelaxationParameter('s_rhox')
    s_qx: RelaxationParameter('s_qx')
    alpha: RealParameter("alpha")
    beta: RealParameter("beta")

    equation = D1_advacoustics()
    dim = 1
    name = 'D1Q33'
    tex_name = r'$D_1Q_{{33}}$'

    def get_required_param(self):
        return [self.equation.c, self.equation.ubar]

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        c = self.equation.c
        u_bar = self.equation.ubar

        # u = q/rho

        la_, la = self.la.symb, self.la.value
        s_rho_, s_rho = self.s_rho.symb, self.s_rho.value
        s_q_, s_q = self.s_q.symb, self.s_q.value
        sigma_rho = sp.symbols('sigma_rho', constants=True)
        sigma_q = sp.symbols('sigma_q', constants=True)
        s_rhox_, s_rhox = self.s_rhox.symb, self.s_rhox.value
        s_qx_, s_qx = self.s_qx.symb, self.s_qx.value
        sigma_rhox = sp.symbols('sigma_rhox', constants=True)
        sigma_qx = sp.symbols('sigma_qx', constants=True)
        alpha_, alpha = self.alpha.symb, self.alpha.value
        beta_, beta = self.beta.symb, self.beta.value

        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': rho,
                    'polynomials': [1, X, X**2/2],
                    'relaxation_parameters': [
                        0, 1/(.5+sigma_rho), 1/(.5+sigma_rhox)
                    ],
                    'equilibrium': [rho, q, alpha_*la_**2*rho/2]
                },
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': q,
                    'polynomials': [1, X, X**2/2],
                    'relaxation_parameters': [
                        0, 1/(.5+sigma_q), 1/(.5+sigma_qx)
                    ],
                    'equilibrium': [
                        q,
                        (c**2-u_bar**2)*rho + 2*u_bar*q,
                        beta_*la_**2*q/2
                    ]
                },
            ],
            'parameters': {
                la_: la,
                s_rho_: s_rho,
                sigma_rho: 1/s_rho_-.5,
                s_q_: s_q,
                sigma_q: 1/s_q_-.5,
                s_rhox_: s_rhox,
                sigma_rhox: 1/s_rhox_-.5,
                s_qx_: s_qx,
                sigma_qx: 1/s_qx_-.5,
                alpha_: alpha,
                beta_: beta,
            },
            'generator': 'numpy'
        }

    def get_boundary(self):
        return {
            self.equation.NonReflexiveOutlet: {
                'method': {
                    0: pylbm.bc.Neumann,
                    1: pylbm.bc.Neumann,
                },
            },
            self.equation.Neumann: {
                'method': {
                    0: pylbm.bc.Neumann,
                    1: pylbm.bc.Neumann,
                },
            },
            self.equation.Dirichlet_u: {
                'method': {
                    0: pylbm.bc.BounceBack,
                    1: pylbm.bc.BounceBack,
                },
            },
        }

