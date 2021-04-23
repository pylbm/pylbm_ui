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


from .equation_type import EquationType, Euler1D
from .exact_solvers import EulerSolver as exact_solver
from .exact_solvers import riemann_pb
from .utils import HashBaseModel

class ToroCase(HashBaseModel):
    rho_left: float
    rho_right: float
    u_left: float
    u_right: float
    p_left: float
    p_right: float
    gamma: float
    duration: float
    xmin: float
    xmax: float
    x_disc: float

    dim=1
    equation = Euler1D()
    name = 'Toro'
    description = 'none'

    def get_dictionary(self):
        q_left = self.rho_left*self.u_left
        q_right = self.rho_right*self.u_right

        e_left = 0.5*self.rho_left*self.u_left**2. \
            + self.p_left/(self.gamma-1.)
        e_right = 0.5*self.rho_right*self.u_right**2. \
            + self.p_right/(self.gamma-1.)

        # zeta_left = self.rho_left*(1./self.gamma)*(np.log(p_left)-self.gamma*np.log(self.rho_left))
        # zeta_right = self.rho_right*(1./self.gamma)*(np.log(p_right)-self.gamma*np.log(self.rho_right))
        zeta_left = 0.
        zeta_right = 0.

        def riemann_pb(x, u_left, u_right):
            vect_u = np.empty(x.shape)
            vect_u[x < self.x_disc] = u_left
            vect_u[x >= self.x_disc] = u_right
            return vect_u

        init = {
            self.equation.rho: (
                    riemann_pb, ( self.rho_left, self.rho_right)
                ),
            self.equation.q: (riemann_pb, ( q_left, q_right)),
        }

        if hasattr(self.equation, 'E'):
            init.update({self.equation.E: (riemann_pb, ( e_left, e_right)),})
        if hasattr(self.equation, 'zeta'):
            init.update({self.equation.zeta: (riemann_pb, ( zeta_left, zeta_right)),})

        return {
            'box': {'x': [self.xmin, self.xmax],
                    'label': [0, 0]
                    },
            'init': init,
            'parameters': {self.equation.gamma: self.gamma}
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
        exact_solution = exact_solver({
            'jump abscissa': self.x_disc,
            'left state': [self.rho_left, self.u_left, self.p_left],
            'right state': [self.rho_right, self.u_right, self.p_right],
            'gamma': self.gamma,
        })
        star_1 = exact_solution.u_star[0]
        star_2 = exact_solution.u_star[1]
        return [{
                    'name': 'Left state',
                    self.equation.rho: self.rho_left,
                    self.equation.q: self.rho_left*self.u_left,
                    self.equation.E: .5*self.rho_left*self.u_left**2 + self.p_left/(self.gamma-1.)
                },
                {
                    'name': 'Right state',
                    self.equation.rho: self.rho_right,
                    self.equation.q: self.rho_right*self.u_right,
                    self.equation.E: .5*self.rho_right*self.u_right**2 + self.p_right/(self.gamma-1.)
                },
                {
                    'name': 'Star 1 state',
                    self.equation.rho: star_1[0],
                    self.equation.q: star_1[0]*star_1[1],
                    self.equation.E: 0.5*star_1[0]*star_1[1]**2. + star_1[2]/(self.gamma-1.)
                },
                {
                    'name': 'Star 2 state',
                    self.equation.rho: star_2[0],
                    self.equation.q: star_2[0]*star_2[1],
                    self.equation.E: 0.5*star_2[0]*star_2[1]**2. + star_2[2]/(self.gamma-1.)
                },
        ]

    def ref_solution(self, t, x, field=None):
        exact_solution = exact_solver({
            'jump abscissa': self.x_disc,
            'left state': [self.rho_left, self.u_left, self.p_left],
            'right state': [self.rho_right, self.u_right, self.p_right],
            'gamma': self.gamma,
        })
        sol_e = exact_solution.evaluate(x, t)

        to_subs = {self.equation.rho: sol_e[0],
                   self.equation.q: sol_e[0]*sol_e[1],
                   self.equation.E: .5*sol_e[0]*sol_e[1]**2 + sol_e[2]/(self.gamma-1.),
                   self.equation.gamma: self.gamma}

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
        sol_e = self.ref_solution(time_e, x_e)

        n_row, n_col = 2, 4
        gs = fig.add_gridspec(n_row, n_col)
        i_row, i_col = 0, 0
        for k, v in sol_e.items():
            ax = fig.add_subplot(gs[i_row, i_col])
            ax.set_title(k)
            ax.plot(x_e, v, color='black')
            i_col += 1
            if i_col == n_col:
                i_col = 0
                i_row += 1


##################################
### predefined cases
##################################
Toro1_1D = ToroCase(
    rho_left=1., rho_right=0.125,
    u_left=0., u_right=0.,
    p_left=1., p_right=0.1,
    gamma=1.4,
    xmin=0., xmax=1, x_disc=0.5,
    duration=0.25,
    name='Toro_1',
    description =
"""
**Toro 1** is the standard Sod shock tube test case.

Left and right states extracted from *Table 4.1 p.129* of the seminal Toro book:

> E.F. Toro. Riemann Solvers and Numerical Methods for Fluid Dynamics: A Practical Introduction. 2nd Edition, Springer, 1999.

The test case parameters can be modified using the "Test case parameters" panel below

The reference final results are computed using exact Riemann solver (???)

\(D_1Q_2\)
"""
    )

Toro2_1D = ToroCase(
    rho_left=1., rho_right=1.,
    u_left=-2., u_right=2.,
    p_left=0.4, p_right=0.4,
    gamma=1.4,
    xmin=0., xmax=1, x_disc=0.5,
    duration=0.15,
    name='Toro_2',
    description =
""" A rarefaction test case
"""
    )

Toro3_1D = ToroCase(
    rho_left=1., rho_right=1.,
    u_left=0., u_right=0.,
    p_left=1000., p_right=0.01,
    gamma=1.4,
    xmin=0., xmax=1, x_disc=0.5,
    duration=0.012,
    name='Toro_3',
    description =
""" A ??? test case
"""
    )

Toro4_1D = ToroCase(
    # rho_left=1., rho_right=0.125,
    # u_left=0., u_right=0.,
    # p_left=0.011, p_right=100.,
    rho_left=1., rho_right=1,
    u_left=0., u_right=0.,
    p_left=0.01, p_right=100.,
    gamma=1.4,
    xmin=0., xmax=1, x_disc=0.5,
    duration=0.035,
    name='Toro_4',
    description =
""" A ??? test case
"""
    )

Toro5_1D = ToroCase(
    rho_left=5.99924, rho_right=5.99242,
    u_left=19.5975, u_right=-6.19633,
    p_left=460.894, p_right=46.0950,
    gamma=1.4,
    xmin=0., xmax=1, x_disc=0.5,
    duration=0.035,
    name='Toro_5',
    description =
""" A ??? test case
"""
    )


