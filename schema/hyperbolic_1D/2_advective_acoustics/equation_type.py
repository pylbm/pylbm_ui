# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#
# License: BSD 3 clause
# from pydantic import BaseModel
import sympy as sp

from ...symbol import Symbol
from ...equation_type import EquationType


class D1_advacoustics(EquationType):
    name = 'Isentropic Advective Acoustics'
    rho = Symbol('rho')
    q = Symbol('q')
    c = Symbol('c')
    ubar = Symbol('u_b')
    NonReflexiveOutlet = 'NonReflexiveOutlet'
    Neumann = 'Neumann'
    Dirichlet_u = 'Dirichlet_u'

    def get_fields(self):
        fields = {
            'mass': self.rho,
            'momentum': self.q,
        }
        return fields
