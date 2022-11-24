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


class D1_acoustics_D1Q3(LBM_scheme):
    s: RelaxationParameter('s')

    equation = D1_acoustics()
    dim = 1
    name = 'D1Q3'
    tex_name = r'$D_1Q_{{}}$'

    def get_required_param(self):
        return [self.equation.c]

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        c = self.equation.c

        # u = q/rho

        la_, la = self.la.symb, self.la.value
        s_, s = self.s.symb, self.s.value
        sigma = sp.symbols('sigma', constants=True)

        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': [rho, q],
                    'polynomials': [1, X, X**2],
                    'relaxation_parameters': [0, 0, 1/(.5+sigma)],
                    'equilibrium': [rho, q, c**2*rho]
                },
            ],
            'parameters': {
                la_: la,
                s_: s,
                sigma: 1/s_-.5,
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

