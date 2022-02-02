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
from ...utils import LBM_scheme, RealParameter, RelaxationParameter


class D1Q3(LBM_scheme):
    s_u: RelaxationParameter('s_u')
    s_ux: RelaxationParameter("s_ux")
    temperature: RealParameter("T")

    equation = Transport1D()
    dim = 1
    name = 'D1Q3'
    tex_name = r'$D_1Q_{{3}}$'

    def get_required_param(self):
        return [self.equation.c]

    def get_dictionary(self):
        u = self.equation.u
        c = self.equation.c

        la_, la = self.la.symb, self.la.value
        s_u_, s_u = self.s_u.symb, self.s_u.value
        s_ux_, s_ux = self.s_ux.symb, self.s_ux.value
        sigma_u = sp.symbols('sigma_u', constants=True)
        sigma_ux = sp.symbols("sigma_ux", constants=True)
        temp_, temp = self.temperature.symb, self.temperature.value

        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': u,
                    'polynomials': [1, X, X**2/2],
                    'relaxation_parameters': [
                        0, 1/(.5+sigma_u), 1/(.5+sigma_ux)
                    ],
                    'equilibrium': [u, c*u, temp_*la_**2*u/2]
                },
            ],
            'parameters': {
                la_: la,
                s_u_: s_u,
                s_ux_: s_ux,
                sigma_u: 1/s_u_-.5,
                sigma_ux: 1/s_ux_-.5,
                temp_: temp,

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

