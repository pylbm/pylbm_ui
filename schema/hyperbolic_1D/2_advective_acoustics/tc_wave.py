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
from ..utils import wave_func_sin
from ...utils import HashBaseModel


class D1_advacoustics_Wave(HashBaseModel):
    k: int
    c: float
    u_bar: float
    duration: float
    xmin: float
    xmax: float

    dim = 1
    equation = D1_advacoustics()
    name = 'Wave for advective acoustics'

    def get_dictionary(self):
        wn = self.k*2*np.pi/(self.xmax-self.xmin)
        omega = wn*(self.c+self.u_bar)
        init = {
            self.equation.rho: (
                wave_func_sin,
                (0, wn, omega, 1)
            ),
            self.equation.q: (
                wave_func_sin,
                (0, wn, omega, self.c+self.u_bar)
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
                'name': 'state',
                self.equation.rho: 0,
                self.equation.q: 0,
                self.equation.c: self.c,
                self.equation.ubar: self.u_bar,
            },
        ]

    def ref_solution(self, t, x, field=None):
        wn = self.k*2*np.pi/(self.xmax-self.xmin)
        omega = wn*(self.c+self.u_bar)
        sol_rho = wave_func_sin(
            x, t, wn, omega, 1
        )
        sol_q = wave_func_sin(
            x, t, wn, omega, self.c+self.u_bar
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

D1_advacoustics_tc_wave = D1_advacoustics_Wave(
    k=1, c=1, u_bar=0.25,
    xmin=0, xmax=1,
    duration=2,
    name='Wave for advective acoustics',
    description_file='./D1_advacoustics_wave.html'
)
