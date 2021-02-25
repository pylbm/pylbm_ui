from pydantic import BaseModel
import pylbm
import matplotlib.gridspec as gridspec
import numpy as np


from .equation_type import EquationType, Euler1D
from .exact_solvers import EulerSolver as exact_solver
from .exact_solvers import riemann_pb

class ToroCase(BaseModel):
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
    responses = {}


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
        return self.xmax-self.xmin

    def state(self):
        return [{self.equation.rho: self.rho_left,
                 self.equation.q: self.rho_left*self.u_left,
                 self.equation.E: .5*self.rho_left*self.u_left**2 + self.p_left/(self.gamma-1.)},
                 {self.equation.rho: self.rho_right,
                 self.equation.q: self.rho_right*self.u_right,
                 self.equation.E: .5*self.rho_right*self.u_right**2 + self.p_right/(self.gamma-1.)},
        ]

    def print_description(self):
        #c_left = np.sqrt(self.gamma*self.p_left/self.rho_left)
        #c_right = np.sqrt(self.gamma*self.p_right/self.rho_right)
        #mach_left = self.u_left / c_left
        #mach_right = self.u_right / c_right
        #print("*"*80)
        #print("Left Mach number:  {:10.7f}".format(mach_left))
        #print("Right Mach number: {:10.7f}".format(mach_right))
        #print("*"*80)
        print(self.description)

    def get_ref_solution(self, t, x, field=None):
        exact_solution = exact_solver({
            'jump abscissa': self.x_disc,
            'left state': [self.rho_left, self.u_left, self.p_left],
            'right state': [self.rho_right, self.u_right, self.p_right],
            'gamma': self.gamma,
        })
        sol_e = exact_solution.evaluate(x, t)

        if field:
            if field == 'mass': return sol_e[0]
            elif field == 'velocity': return sol_e[1]
            elif field == 'pressure': return sol_e[2]
            elif field == 'momentum': return sol_e[0]*sol_e[1]
            elif field == 'energy': return .5*sol_e[0]*sol_e[1]**2 + sol_e[2]/(self.gamma-1.)
            elif field == 'internal energy': return sol_e[2]/sol_e[0]/(self.gamma-1)
            elif field == 'Mach number': return  np.sqrt((sol_e[0]*sol_e[1])**2/(self.gamma*sol_e[0]*sol_e[2]))
            else: print("ERROR IN get_exact_solution")

        return sol_e

    def plot_ref_solution(self, fig):
        x_e = np.linspace(self.xmin, self.xmax, 1000)
        time_e = self.duration
        sol_e = self.get_ref_solution(time_e, x_e)

        rho_e = sol_e[0]
        u_e = sol_e[1]
        p_e = sol_e[2]
        q_e = rho_e * u_e
        rhoe_e = .5*rho_e*u_e**2 + p_e/(self.gamma-1.)
        e_e = p_e/rho_e/(self.gamma-1)
        mach_e = np.sqrt(q_e**2/(self.gamma*rho_e*p_e))

        gs = fig.add_gridspec(2, 4)
        gs.update(wspace=0.3, hspace=0.3)
        ax = fig.add_subplot(gs[0, 0])
        ax.set_title('Mass')
        ax.plot(x_e, rho_e, color='black')

        ax = fig.add_subplot(gs[0, 1])
        ax.set_title('Velocity')
        ax.plot(x_e, u_e, color='black')

        ax = fig.add_subplot(gs[0, 2])
        ax.set_title('Pressure')
        ax.plot(x_e, p_e, color='black')

        ax = fig.add_subplot(gs[0, 3])
        ax.set_title('Energy')
        ax.plot(x_e, rhoe_e, color='black')

        ax = fig.add_subplot(gs[1, 0])
        ax.set_title('Momentum')
        ax.plot(x_e, q_e, color='black')

        ax = fig.add_subplot(gs[1, 1])
        ax.set_title('Internal energy')
        ax.plot(x_e, e_e, color='black')

        ax = fig.add_subplot(gs[1, 2])
        ax.set_title('Mach number')
        ax.plot(x_e, mach_e, color='black')

    def plot(self, sol=None):
        xmid = .5*(self.xmin + self.xmax)
        exact_solution = exact_solver({
            'jump abscissa': xmid,
            'left state': [self.rho_left, self.u_left, self.p_left],
            'right state': [self.rho_right, self.u_right, self.p_right],
            'gamma': self.gamma,
        })
        x_e = np.linspace(self.xmin, self.xmax, 1000)
        sol_e = exact_solution.evaluate(x_e, self.duration)

        viewer = pylbm.viewer.matplotlib_viewer
        fig = viewer.Fig(2, 4, figsize=(12, 8))
        list_color = ['navy', 'orange', 'green', 'purple']
        list_symb = ['^', '<', 'v', '>']

        rho_e = sol_e[0]
        u_e = sol_e[1]
        p_e = sol_e[2]
        q_e = rho_e * u_e
        rhoe_e = .5*rho_e*u_e**2 + p_e/(self.gamma-1.)
        e_e = p_e/rho_e/(self.gamma-1)
        mach_e = np.sqrt(q_e**2/(self.gamma*rho_e*p_e))

        fig[0, 0].CurveLine(x_e, rho_e, color='black', width=1)
        fig[0, 0].title = 'mass'
        fig[0, 1].CurveLine(x_e, u_e, color='black', width=1)
        fig[0, 1].title = 'velocity'
        fig[0, 2].CurveLine(x_e, p_e, color='black', width=1)
        fig[0, 2].title = 'pressure'
        fig[1, 0].CurveLine(x_e, rhoe_e, color='black', width=1)
        fig[1, 0].title = 'energy'
        fig[1, 1].CurveLine(x_e, q_e, color='black', width=1)
        fig[1, 1].title = 'momentum'
        fig[1, 2].CurveLine(x_e, e_e, color='black', width=1)
        fig[1, 2].title = 'internal energy'
        fig[1, 3].CurveLine(x_e, mach_e, color='black', width=1)
        fig[1, 3].title = 'Mach number'

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


