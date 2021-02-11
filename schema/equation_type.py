from pydantic import BaseModel
from .symbol import Symbol
import sympy as sp

class EquationType(BaseModel):
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

# class NS1D(EquationType):
#     rho: sp.Symbol = field(init=False, default=sp.symbols('rho'))
#     q: sp.Symbol = field(init=False, default=sp.symbols('q'))
#     zeta: sp.Symbol = field(init=False, default=sp.symbols('zeta'))
#     gamma: sp.Symbol = field(init=False, default=sp.symbols('gamma'))
#     prandtl: sp.Symbol = field(init=False, default=sp.symbols('prandtl'))
#     NonReflexiveOutlet: str = field(init=False, default='NonReflexiveOutlet')
#     Neumann: str = field(init=False, default='Neumann')
#     Dirichlet_u: str = field(init=False, default='Dirichlet_u')
