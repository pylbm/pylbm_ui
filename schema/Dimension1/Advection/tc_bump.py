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
from ..utils import bump as bump_init
from ...utils import HashBaseModel


class Bump(HashBaseModel):
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
                bump_init,
                (
                    self.reg,
                    self.x_top, self.width_bump,
                    self.u_bottom, self.u_top
                )
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
                self.equation.u: self.u_bottom,
                self.equation.c: self.c,
            },
            {
                'name': 'Bump state',
                self.equation.u: self.u_top,
                self.equation.c: self.c,
            },
        ]

    def ref_solution(self, t, x, field=None):
        xloc = self.xmin + (x - self.c*t - self.xmin) % (self.xmax-self.xmin)
        sol_e = bump_init(
            xloc,
            self.reg,
            self.x_top, self.width_bump,
            self.u_bottom, self.u_top
        )
        return sol_e

    def plot_ref_solution(self, fig):
        x_e = np.linspace(self.xmin, self.xmax, 1000)
        time_e = self.duration
        sol_i = self.ref_solution(0, x_e)
        sol_e = self.ref_solution(time_e, x_e)
        n_row, n_col = 1, 1
        gs = fig.add_gridspec(n_row, n_col)
        ax = fig.add_subplot(gs[0, 0])
        ax.set_title(r'$u$')
        ax.plot(
            x_e, sol_i, alpha=0.5,
            linewidth=2,
            color='navy', label=f'$t=0$'
        )
        ax.plot(
            x_e, sol_e, alpha=0.5,
            linewidth=2,
            color='orange', label=f'$t={time_e}$'
        )
        ax.legend()


##################################
### predefined cases
##################################


Bump_discont = Bump(
    u_bottom=0, u_top=1,
    c=1, reg=-1,
    xmin=0, xmax=1,
    x_top=0.25, width_bump=0.125,
    duration=1.5,
    name='Bump discontinuous',
    description="""
Une description du cas test pour voir

Mettre que l'on a des conditions aux limites périodiques
    """
)


Bump_C0 = Bump(
    u_bottom=0, u_top=1,
    c=1, reg=0,
    xmin=0, xmax=1,
    x_top=0.25, width_bump=0.125,
    duration=1.5,
    name='Bump C0',
    description=""
)


Bump_C1 = Bump(
    u_bottom=0, u_top=1,
    c=1, reg=1,
    xmin=0, xmax=1,
    x_top=0.25, width_bump=0.125,
    duration=1.5,
    name='Bump C1',
    description=""
)
