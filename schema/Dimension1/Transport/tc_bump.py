# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
import pylbm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import sympy as sp

from .equation_type import Transport1D
#from .exact_solvers
from ..utils import bump
from ...utils import HashBaseModel


class bump(HashBaseModel):
    u_bottom: float
    u_top: float
    c: float
    duration: float
    xmin: float
    xmax: float
    x_top: float
    width_bump: float
    reg: int

    dim = 1
    equation = Transport1D()
    name = 'Bump'
    description = 'none'

    def get_dictionary(self):
        init = {
            self.equation.u: (
                bump,
                (self.reg, self.x_top, self.width_bump)
            )
        }
        return {
            'box': {
                'x': [self.xmin, self.xmax],
                'label': -1
            },
            'init': init,
            'parameters': {self.equation.c: self.c},
        }

    def get_boundary(self):
        return {
            0: self.equation.NonReflexiveOutlet,
        }

    def size(self):
        return [self.xmax - self.xmin]

    def set_size(self, size):
        self.xmax = self.xmin + size[0]

    def state(self):
        return [
            {
                'name': 'Ground state',
                self.equation.u: 0,
            },
            {
                'name': 'Bump state',
                self.equation.u: 1,
            },
        ]

# def ref_solution(self, t, x, field=None):


##################################
### predefined cases
##################################

Bump_discont = bump(
    u_bottom=0, u_top=1,
    c=1, reg=1,
    xmin=0, xmax=1,
    x_top=0.25, width_bump=0.125,
    duration=2,
    name='Bump_disc',
    description=""
)
