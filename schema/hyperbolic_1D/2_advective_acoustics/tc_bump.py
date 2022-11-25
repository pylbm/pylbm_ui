# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#
# License: BSD 3 clause
import pylbm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import sympy as sp

from .equation_type import D1_advacoustics
from ..utils import bump as bump_init
from ...utils import HashBaseModel


class D1_advacoustics_Bump(HashBaseModel):
    rho_ground: float
    rho_bump: float
    u_zero: float
    c: float
    u_bar: float
    duration: float
    xmin: float
    xmax: float
    x_bump: float
    width_bump: float
    reg: int

    dim = 1
    equation = D1_advacoustics()
    name = 'Bump for advective acoustics'

    def get_dictionary(self):
        init = {
            self.equation.rho: (
                bump_init,
                (
                    self.reg,
                    self.x_bump, self.width_bump,
                    self.rho_ground, self.rho_bump
                )
            ),
            self.equation.q: (
                bump_init,
                (
                    self.reg,
                    self.x_bump, self.width_bump,
                    self.rho_ground*self.u_zero,
                    self.rho_bump*self.u_zero
                )
            )
        }

        return {
            'box': {
                'x': [self.xmin, self.xmax],
                'label': -1
            },
            'init': init,
            'parameters': {
                self.equation.c: self.c,
                self.equation.ubar: self.u_bar,
            },
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
                self.equation.rho: self.rho_ground,
                self.equation.q: self.rho_ground*self.u_zero,
                self.equation.c: self.c,
                self.equation.ubar: self.u_bar,
            },
            {
                'name': 'Bump state',
                self.equation.rho: self.rho_bump,
                self.equation.q: self.rho_bump*self.u_zero,
                self.equation.c: self.c,
                self.equation.ubar: self.u_bar,
            },
        ]

    def ref_solution(self, t, x, field=None):
        v_l = self.u_bar - self.c
        v_r = self.u_bar + self.c
        xloc_l = self.xmin + (x - v_l*t - self.xmin) % (self.xmax-self.xmin)
        xloc_r = self.xmin + (x - v_r*t - self.xmin) % (self.xmax-self.xmin)
        sol_rho = .5/self.c * (
            (v_r-self.u_zero) * bump_init(
                xloc_l,
                self.reg,
                self.x_bump, self.width_bump,
                self.rho_ground, self.rho_bump
            ) - 
            (v_l-self.u_zero) * bump_init(
                xloc_r,
                self.reg,
                self.x_bump, self.width_bump,
                self.rho_ground, self.rho_bump
            )
        )
        sol_q = .5/self.c * (
            v_r * (v_l+self.u_zero) * bump_init(
                xloc_l,
                self.reg,
                self.x_bump, self.width_bump,
                self.rho_ground, self.rho_bump
            ) - 
            v_l * (v_r+self.u_zero) * bump_init(
                xloc_r,
                self.reg,
                self.x_bump, self.width_bump,
                self.rho_ground, self.rho_bump
            )
        )

        to_subs = {
            self.equation.rho: sol_rho,
            self.equation.q: sol_q,
        }

        if field:
            expr = self.equation.get_fields()[field]
            args = {str(s): to_subs[s] for s in expr.atoms(sp.Symbol)}
            func = sp.lambdify(list(expr.atoms(sp.Symbol)), expr, "numpy", dummify=False)
            output = func(**args)
        else:
            output = {}
            for k, v in self.equation.get_fields().items():
                args = {str(s): to_subs[s] for s in v.atoms(sp.Symbol)}
                func = sp.lambdify(list(v.atoms(sp.Symbol)), v, "numpy", dummify=False)
                output[k] = func(**args)
    
        return output

    def plot_ref_solution(self, fig):
        x_e = np.linspace(self.xmin, self.xmax, 1000)
        time_e = self.duration
        sol_i = self.ref_solution(0, x_e)
        sol_e = self.ref_solution(time_e, x_e)
        n_row, n_col = 2, 1
        gs = fig.add_gridspec(n_row, n_col)

        i_row, i_col = 0, 0
        for k, v in sol_e.items():
            ax = fig.add_subplot(gs[i_row, i_col])
            ax.set_title(k)
            ax.plot(
                x_e, v,
                linewidth=2, alpha=0.5,
                color='orange', label=f"$t={time_e}$"
            )
            ax.plot(
                x_e, sol_i[k],
                linewidth=2, alpha=0.5,
                color='navy', label=f"$t=0$"
            )
            ax.legend()
            i_col += 1
            if i_col == n_col:
                i_col = 0
                i_row += 1


##################################
### predefined cases
##################################

D1_advacoustics_tc_bumpy = D1_advacoustics_Bump(
    rho_ground=0, rho_bump=1,
    u_zero=0, u_bar=0.25,
    c=1, reg=0,
    xmin=0, xmax=1,
    x_bump=0.5, width_bump=0.125,
    duration=0.25,
    name='Bump for advective acoustics',
    description_file='./D1_advacoustics_bump.html'
)
