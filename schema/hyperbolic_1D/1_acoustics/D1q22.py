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
from .equation_type import D1_acoustics
from ...utils import LBM_scheme, RelaxationParameter


class D1_acoustics_D1Q22(LBM_scheme):
    s_rho: RelaxationParameter('s_rho')
    s_q: RelaxationParameter('s_q')

    equation = D1_acoustics()
    dim = 1
    name = 'D1Q22'
    tex_name = r'$D_1Q_{{22}}$'

    def get_required_param(self):
        return [self.equation.c]

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        c = self.equation.c

        u = q/rho

        la_, la = self.la.symb, self.la.value
        s_rho_, s_rho = self.s_rho.symb, self.s_rho.value
        s_q_, s_q = self.s_q.symb, self.s_q.value
        sigma_rho = sp.symbols('sigma_rho', constants=True)
        sigma_q = sp.symbols('sigma_q', constants=True)

        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': [1, 2],
                    'conserved_moments': rho,
                    'polynomials': [1, X],
                    'relaxation_parameters': [0, 1/(.5+sigma_rho)],
                    'equilibrium': [rho, q]
                },
                {
                    'velocities': [1, 2],
                    'conserved_moments': q,
                    'polynomials': [1, X],
                    'relaxation_parameters': [0, 1/(.5+sigma_q)],
                    'equilibrium': [q, c**2*rho]
                },
            ],
            'parameters': {
                la_: la,
                s_rho_: s_rho,
                sigma_rho: 1/s_rho_-.5,
                s_q_: s_q,
                sigma_q: 1/s_q_-.5,
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
                    # 1: pylbm.bc.AntiBounceBack,
                    # 2: pylbm.bc.BounceBack,
                },
            },
        }

