# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
from pydantic import BaseModel
import sympy as sp

from ...symbol import Symbol
from ...equation_type import EquationType


class Euler2D(EquationType):
    rho = Symbol('rho')
    qx = Symbol('q_x')
    qy = Symbol('q_y')
    E = Symbol('E')
    gamma = Symbol('gamma')
    NonReflexiveOutlet='NonReflexiveOutlet'
    Neumann='Neumann'
    Dirichlet_u='Dirichlet_u'
    Symmetry_X='Symmetry_X'
    Symmetry_Y='Symmetry_Y'

    def get_fields(self):
        fields = {'mass': self.rho,
                  'momentum in x': self.qx,
                  'momentum in y': self.qy,
                  'energy': self.E,
                  'velocity in x': self.qx/self.rho,
                  'velocity in y': self.qy/self.rho,
                  'pressure': (self.gamma-1)*(self.E - 0.5*(self.qx**2 + self.qy**2)/self.rho),
                  'internal energy': self.E/self.rho - 0.5*(self.qx**2 + self.qy**2)/self.rho**2,
        }
        fields['mach number'] = sp.sqrt((self.qx**2 + self.qy**2)/(self.gamma*self.rho*fields['pressure']))

        return fields


# class NS1D(EquationType):
#     rho: sp.Symbol = field(init=False, default=sp.symbols('rho'))
#     q: sp.Symbol = field(init=False, default=sp.symbols('q'))
#     zeta: sp.Symbol = field(init=False, default=sp.symbols('zeta'))
#     gamma: sp.Symbol = field(init=False, default=sp.symbols('gamma'))
#     prandtl: sp.Symbol = field(init=False, default=sp.symbols('prandtl'))
#     NonReflexiveOutlet: str = field(init=False, default='NonReflexiveOutlet')
#     Neumann: str = field(init=False, default='Neumann')
#     Dirichlet_u: str = field(init=False, default='Dirichlet_u')
