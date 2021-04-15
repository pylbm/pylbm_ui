# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
from pydantic import BaseModel
import sympy as sp

from .symbol import Symbol
from .utils import HashBaseModel

class EquationType(HashBaseModel):
    pass


class Euler1D(EquationType):
    rho = Symbol('rho')
    q = Symbol('q')
    E = Symbol('E')
    gamma = Symbol('gamma')
    NonReflexiveOutlet='NonReflexiveOutlet'
    Neumann='Neumann'
    Dirichlet_u='Dirichlet_u'

    def get_fields(self):
        fields = {'mass': self.rho,
                  'momentum': self.q,
                  'energy': self.E,
                  'velocity': self.q/self.rho,
                  'pressure': (self.gamma-1)*(self.E - self.q**2/self.rho/2),
                  'internal energy': self.E/self.rho - self.q**2/self.rho**2/2,
        }
        fields['mach number'] = sp.sqrt(self.q**2/(self.gamma*self.rho*fields['pressure']))

        return fields

class Euler2D(EquationType):
    rho = Symbol('rho')
    qx = Symbol('qx')
    qy = Symbol('qy')
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
