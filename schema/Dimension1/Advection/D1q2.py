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
from .equation_type import Transport1D
from ...utils import LBM_scheme, RelaxationParameter


class D1Q2(LBM_scheme):
    s_u: RelaxationParameter('s_u')

    equation = Transport1D()
    dim = 1
    name = 'D1Q2'
    tex_name = r'$D_1Q_{{2}}$'

    def get_required_param(self):
        return [self.equation.c]

    def get_dictionary(self):
        u = self.equation.u
        c = self.equation.c

        la_, la = self.la.symb, self.la.value
        s_u_, s_u = self.s_u.symb, self.s_u.value
        sigma_u = sp.symbols('sigma_u', constants=True)

        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': [1, 2],
                    'conserved_moments': u,
                    'polynomials': [1, X],
                    'relaxation_parameters': [0, 1/(.5+sigma_u)],
                    'equilibrium': [u, c*u]
                },
            ],
            'parameters': {
                la_: la,
                s_u_: s_u,
                sigma_u: 1/s_u_-.5,

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
                    # 1: pylbm.bc.AntiBounceBack,
                    # 2: pylbm.bc.BounceBack,
                },
            },
        }

