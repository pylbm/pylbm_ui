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

from .equation_type import D1_advection
from ..utils import indicator as indicator_init
from ...utils import HashBaseModel


class D1_advection_Indicator(HashBaseModel):
    u_out: float
    u_in: float
    c: float
    duration: float
    xmin: float
    xmax: float
    pos_left: float
    width_left: float
    pos_right: float
    width_right: float
    reg: int

    dim = 1
    equation = D1_advection()
    name = 'Indicator for advection'

    def get_dictionary(self):
        init = {
            self.equation.u: (
                indicator_init,
                (
                    self.reg,
                    self.pos_left, self.pos_right,
                    self.width_left, self.width_right,
                    self.u_out, self.u_in
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
                self.equation.u: self.u_out,
                self.equation.c: self.c,
            },
            {
                'name': 'Bump state',
                self.equation.u: self.u_in,
                self.equation.c: self.c,
            },
        ]

    def ref_solution(self, t, x, field=None):
        xloc = self.xmin + (x - self.c*t - self.xmin) % (self.xmax-self.xmin)
        sol_e = indicator_init(
            xloc,
            self.reg,
            self.pos_left, self.pos_right,
            self.width_left, self.width_right,
            self.u_out, self.u_in
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

D1_advection_tc_indy = D1_advection_Indicator(
    u_out=0, u_in=1,
    c=1, reg=1,
    xmin=0, xmax=1,
    pos_left=0.2, pos_right=0.4,
    width_left=0.05, width_right=0.05,
    duration=1.5,
    name='Indicator for advection',
    description_file='./D1_advection_indicator.html'
)
