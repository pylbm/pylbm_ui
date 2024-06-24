# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
# from pydantic import BaseModel
import sympy as sp

from ...symbol import Symbol
from ...equation_type import EquationType


class D1_advection(EquationType):
    name = 'Advection with constant velocity'
    u = Symbol('u')
    c = Symbol('c')
    NonReflexiveOutlet = 'NonReflexiveOutlet'
    Neumann = 'Neumann'
    Dirichlet_u = 'Dirichlet_u'

    def get_fields(self):
        fields = {
            'mass': self.u,
        }
        return fields

