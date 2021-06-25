# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
import pylbm
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import sympy as sp
import hashlib

from .equation_type import Euler2D
from ...utils import HashBaseModel


def borne_sup(f, a, b_max):
    fa = f(a)
    b = b_max
    fb = f(b)
    h = 1
    while fa*fb > 0 and h > 1.e-14:
        h = .5*(b_max-a)
        b_new = b-h
        while fa*fb < fa*f(b_new):
            h /= 2
            b_new = b-h
        b, fb = b_new, f(b_new)
    return b


def dichotomie(f, a, b_max, epsilon=1.e-10):
    """Dichotomie to solve f(x)=0 in [a, b]"""
    b = borne_sup(f, a, b_max)
    fa, fb = f(a), f(b)
    c = .5*(a+b)
    fc = f(c)
    if fa*fb > 0:
        return np.nan
    while b - a > epsilon:
        if fa*fc >= 0:
            a, fa = c, fc
        if fb*fc >= 0:
            b, fb = c, fc
        c = .5*(a+b)
        fc = f(c)
    return c


class exact_solver:
    """
    exact solver for the wedge
    """
    def __init__(self, config):
        """Compute the outlet values being given the inlet values"""
        theta = config['angle_degre'] * np.pi / 180
        rho_in, ux_in, p_in = config['inlet']
        gamma = config['gamma']

        # the function that gives the shock angle
        def f_alpha(alpha):
            st = np.sin(theta)
            ca = np.cos(alpha)
            ta = np.tan(alpha)
            cda = ca*ca
            samt = np.sin(alpha-theta)
            cdamt = np.cos(alpha-theta)**2
            tamt = np.tan(alpha-theta)
            return rho_in*ux_in**2*(
                .5*(cdamt - cda) - gamma/(gamma-1)*ca*st*samt
            ) / cdamt - gamma/(gamma-1)*p_in*(
                tamt - ta
            ) / ta

        alpha = dichotomie(f_alpha, theta, 1.2)
        if np.isnan(alpha):
            return alpha, None, None, None, None
        rho = rho_in * np.tan(alpha) / np.tan(alpha-theta)
        v = ux_in * np.cos(alpha) / np.cos(alpha-theta)
        p = p_in + rho_in*ux_in**2 * np.sin(alpha)*np.sin(theta) \
            / np.cos(alpha-theta)
        ux = v * np.cos(theta)
        uy = v * np.sin(theta)

        self.theta, self.alpha = theta, alpha
        self.rho_in, self.ux_in, self.uy_in, self.p_in = rho_in, ux_in, 0, p_in
        self.rho_out, self.ux_out, self.uy_out, self.p_out = rho, ux, uy, p
        self.posx = config['position_wedge']
        self.sol = np.array([])

    def evaluate(self, x, y, t):
        if self.sol.shape != (4, x.size, y.size):
            self.sol = np.zeros((4, x.size, y.size))
            rho = self.sol[0]
            ux = self.sol[1]
            uy = self.sol[2]
            p = self.sol[3]
            ind_out = y[None, :] <= (x[:, None]-self.posx) * np.tan(self.alpha)
            rho[:] = self.rho_in + (self.rho_out-self.rho_in) * ind_out
            ux[:] = self.ux_in + (self.ux_out-self.ux_in) * ind_out
            uy[:] = self.uy_in + (self.uy_out-self.uy_in) * ind_out
            p[:] = self.p_in + (self.p_out-self.p_in) * ind_out
        return self.sol


cache_exact_solver = {}
class tc_2D_wedge(HashBaseModel):
    xmin: float
    xmax: float
    ymin: float
    ymax: float

    rho_in: float
    ux_in: float
    uy_in: float
    p_in: float

    angle_degre: float

    gamma: float
    duration: float

    distance_relative = 0.2
    dim = 2
    # angle_degre = 15
    equation = Euler2D()
    name = 'Wedge2D'
    BCType = 'none'
    # description = 'none'
    responses = {}

    def get_dictionary(self):

        def init_rho(x, y):
            return self.rho_in

        def init_ux(x, y):
            return self.ux_in

        def init_uy(x, y):
            return self.uy_in

        def init_p(x, y):
            return self.p_in

        def init_qx(x, y):
            return init_rho(x, y) * init_ux(x, y)

        def init_qy(x, y):
            return init_rho(x, y) * init_uy(x, y)

        def init_E(x, y):
            return .5*init_rho(x, y) * (
                init_ux(x, y)**2 + init_uy(x, y)
                ) + init_p(x, y)/(self.gamma-1)

        BC_labels = [1, 1, 4, 1]

        angle = self.angle_degre * np.pi / 180
        posx = self.xmin + (self.xmax-self.xmin)*self.distance_relative
        tri_p1 = [posx, self.ymin]
        tri_p2 = [self.xmax, (self.xmax - posx)*np.tan(angle)]
        tri_p3 = [self.xmax, self.ymin]

        return {
            'box': {
                'x': [self.xmin, self.xmax],
                'y': [self.ymin, self.ymax],
                'label': BC_labels
            },
            'elements': [
                pylbm.Triangle(
                    (tri_p1[0], tri_p1[1]),
                    (tri_p2[0], tri_p2[1]),
                    (tri_p3[0], tri_p3[1]),
                    label=2
                )
            ],
            'init': {
                self.equation.rho: init_rho,
                self.equation.qx: init_qx,
                self.equation.qy: init_qy,
                self.equation.E: init_E,
            },
            'parameters': {
                self.equation.gamma: self.gamma
            }
        }

    def size(self):
        return [self.xmax - self.xmin, self.ymax - self.ymin]

    def set_size(self, size):
        self.xmax = self.xmin + size[0]
        self.ymax = self.ymin + size[1]

    def get_boundary(self):
        return {
            0: self.equation.NonReflexiveOutlet,
            1: self.equation.Neumann,
            2: self.equation.Dirichlet_u,
            3: self.equation.Symmetry_Y,
            4: self.equation.Symmetry_X
        }

    def state(self):
        return [
            {
                self.equation.rho: self.rho_in,
                self.equation.qx: self.rho_in*self.ux_in,
                self.equation.qy: self.rho_in*self.uy_in,
                self.equation.E: 0.5*self.rho_in*(
                    self.ux_in**2.*self.uy_in**2.
                ) + self.p_in/(self.gamma-1.),
            },
        ]

    def get_exact_solution(self):
        config = {
            'angle_degre': self.angle_degre,
            'inlet': [self.rho_in, self.ux_in, self.p_in],
            'gamma': self.gamma,
            'position_wedge': self.xmin + (self.xmax-self.xmin)*self.distance_relative
        }

        dhash = hashlib.md5()
        dhash.update(f'{config.values()}'.encode())
        hash = dhash.hexdigest()

        if hash not in cache_exact_solver:
            cache_exact_solver[hash] = exact_solver(config)

        return cache_exact_solver[hash]

    def ref_solution(self, t, x, y, field=None):
        exact_solution = self.get_exact_solution()
        sol_e = exact_solution.evaluate(x, y, t)
        rho = sol_e[0]
        ux, uy = sol_e[1], sol_e[2]
        p = sol_e[3]

        to_subs = {
            self.equation.rho: rho,
            self.equation.qx: rho*ux,
            self.equation.qy: rho*uy,
            self.equation.E: .5*rho*(ux**2+uy**2)+p/(self.gamma-1.),
            self.equation.gamma: self.gamma
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
        exact_solution = self.get_exact_solution()
        angle = exact_solution.theta
        posx = exact_solution.posx
        alpha = exact_solution.alpha
        rho_out = exact_solution.rho_out
        ux_out, uy_out = exact_solution.ux_out, exact_solution.uy_out
        p_out = exact_solution.p_out

        # initialize the figure
        gs = fig.add_gridspec(1, 1)
        ax = fig.add_subplot(gs[0, 0])
        ax.set_title(f"Wedge $\\theta={self.angle_degre}^\circ : \\beta = {alpha*180/np.pi:.3f}^\circ$")
        ax.set_xlim(self.xmin, self.xmax)
        ax.set_ylim(self.ymin, self.ymax)
        # plot the wedge
        ax.plot(
            [posx, self.xmax],
            [self.ymin, self.ymin+(self.xmax-posx)*np.tan(angle)],
            color='black', alpha=1, linewidth=1
        )
        pos = [
            [posx, self.ymin],
            [self.xmax, self.ymin],
            [self.xmax, self.ymin+(self.xmax-posx)*np.tan(angle)]
        ]
        ax.add_patch(
            Polygon(
                pos,
                closed=True, fill=True, color='black', alpha=0.5,
                # zorder=0
            )
        )
        if not np.isnan(alpha):
            # plot the outlet
            pos = [
                [posx, self.ymin],
                [self.xmax, self.ymin+(self.xmax-posx)*np.tan(angle)],
                [self.xmax, self.ymin+(self.xmax-posx)*np.tan(alpha)]
            ]
            ax.add_patch(
                Polygon(
                    pos,
                    closed=True, fill=True, color='blue', alpha=0.5,
                    # zorder=0
                )
            )
            # plot the inlet
            pos = [
                [self.xmin, self.ymin],
                [posx, self.ymin],
                [self.xmax, self.ymin+(self.xmax-posx)*np.tan(alpha)],
                [self.xmax, self.ymax],
                [self.xmin, self.ymax]
            ]
            ax.add_patch(
                Polygon(
                    pos,
                    closed=True, fill=True, color='red', alpha=0.5,
                    # zorder=0
                )
            )
            t = 10
            decalx = 0.25*(self.xmax-self.xmin)
            decaly = 0.1*(self.ymax-self.ymin)
            noms = ['rho', 'v', 'p', 'Ma']
            v_in = np.sqrt(self.ux_in**2 + self.uy_in**2)
            c_in = np.sqrt(self.gamma*self.p_in/self.rho_in)
            Ma_in = v_in / c_in
            val_in = [
                self.rho_in,
                v_in,
                self.p_in,
                Ma_in
            ]
            v_out = np.sqrt(ux_out**2 + uy_out**2)
            c_out = np.sqrt(self.gamma*p_out/rho_out)
            Ma_out = v_out / c_out
            val_out = [
                rho_out, v_out, p_out, Ma_out
            ]
            ky = 1
            for nom, vin, vout in zip(noms, val_in, val_out):
                n = int(np.log10(max(vin, vout))) + 1
                d = t - 2 - n
                msg = f"{nom}_in = {vin:{n}.{d}f}"
                posy = self.ymax - ky*decaly
                ax.text(
                    posx, posy,
                    msg,
                    color='black',
                    horizontalalignment='left',verticalalignment='center',
                    fontsize=12
                )
                msg = f"{nom}_out = {vout:{n}.{d}f}"
                ax.text(
                    posx + decalx, posy,
                    msg,
                    color='black',
                    horizontalalignment='left',verticalalignment='center',
                    fontsize=12
                )
                ky += 1
        ax.grid(False)

##################################
### predefined cases
##################################

Wedge_Ma2p5 = tc_2D_wedge(
    name='Wedge_Ma2p5',
    xmin=0., xmax=3.,
    ymin=0., ymax=2.,
    angle_degre=15,
    rho_in=1.4,
    ux_in=2.5,
    uy_in=0.,
    p_in=1.,
    gamma=1.4,
    duration=5.,
    description_file='./wedge.html'
)

Wedge_Ma8 = tc_2D_wedge(
    name='Wedge_Ma8',
    xmin=0., xmax=3.,
    ymin=0., ymax=2.,
    angle_degre=15,
    rho_in=1.4,
    ux_in=8,
    uy_in=0.,
    p_in=1.,
    gamma=1.4,
    duration=5.,
    description_file='./wedge.html'
)
