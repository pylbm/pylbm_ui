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


class Euler1D(EquationType):
    rho = Symbol('rho')
    q = Symbol('q')
    E = Symbol('E')
    gamma = Symbol('gamma')
    NonReflexiveOutlet = 'NonReflexiveOutlet'
    Neumann = 'Neumann'
    Dirichlet_u = 'Dirichlet_u'

    def get_fields(self):
        gamma_ = self.gamma
        fields = {
            'mass': self.rho,
            'momentum': self.q,
            'energy': self.E,
            'velocity': self.q/self.rho,
            'pressure': (gamma_-1)*(self.E - self.q**2/self.rho/2),
            'internal energy': self.E/self.rho - self.q**2/self.rho**2/2,
        }
        fields['mach number'] = sp.sqrt(
            self.q**2/(gamma_*self.rho*fields['pressure'])
        )

        return fields

    @property
    def description(self):
        return ""