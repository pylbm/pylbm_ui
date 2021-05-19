# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
from pydantic import BaseModel
import sympy as sp
import pylbm
from .equation_type import Euler1D
from ...utils import LBM_scheme, RelaxationParameter


class D1Q333_general(LBM_scheme):
    s_rho: RelaxationParameter('s_rho')
    s_u: RelaxationParameter('s_u')
    s_p: RelaxationParameter('s_p')
    s_rhox: RelaxationParameter('s_rhox')
    s_ux: RelaxationParameter('s_ux')
    s_px: RelaxationParameter('s_px')

    equation = Euler1D()
    dim = 1
    name = 'D1Q333_gen'
    tex_name = r'$D_1Q_{{333}}$_gen'
    description_file='./d1q333.html'

    addvisc = 0.

    def get_required_param(self):
        return [self.equation.gamma]

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        E = self.equation.E
        gamma = self.equation.gamma
        u = q/rho              # velocity

        sigma_rho = sp.symbols('sigma_rho', constants=True)
        sigma_u = sp.symbols('sigma_u', constants=True)
        sigma_p = sp.symbols('sigma_p', constants=True)
        sigma_rhox = sp.symbols('sigma_rhox', constants=True)
        sigma_ux = sp.symbols('sigma_ux', constants=True)
        sigma_px = sp.symbols('sigma_px', constants=True)

        la_, la = self.la.symb, self.la.value
        s_rho_, s_rho = self.s_rho.symb, self.s_rho.value
        s_u_, s_u = self.s_u.symb, self.s_u.value
        s_p_, s_p = self.s_p.symb, self.s_p.value
        s_rhox_, s_rhox = self.s_rhox.symb, self.s_rhox.value
        s_ux_, s_ux = self.s_ux.symb, self.s_ux.value
        s_px_, s_px = self.s_px.symb, self.s_px.value

        symb_s_rho = 1/(.5+sigma_rho)      # symbolic relaxation parameter
        symb_s_u = 1/(.5+sigma_u)          # symbolic relaxation parameter
        symb_s_p = 1/(.5+sigma_p)          # symbolic relaxation parameter
        symb_s_rhox = 1/(.5+sigma_rhox)    # symbolic relaxation parameter
        symb_s_ux = 1/(.5+sigma_ux)        # symbolic relaxation parameter
        symb_s_px = 1/(.5+sigma_px)        # symbolic relaxation parameter

        # equilibrium values
        w0eq, w1eq, w2eq = self._get_equilibrium(
            rho, q, E, gamma
        )
        # add numerical diffusion
        addvisc = self.addvisc
        w0eq = (1-addvisc)*w0eq + addvisc/2*la**2*rho
        w1eq = (1-addvisc)*w1eq + addvisc/2*la**2*q
        w2eq = (1-addvisc)*w2eq + addvisc/2*la**2*E

        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': rho,
                    'polynomials': [1, X, X**2/2],
                    'relaxation_parameters': [0, symb_s_rho, symb_s_rhox],
                    'equilibrium': [
                        rho,
                        q,
                        w0eq
                    ]
                },
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': q,
                    'polynomials': [1, X, X**2/2],
                    'relaxation_parameters': [0, symb_s_u, symb_s_ux],
                    'equilibrium': [
                        q,
                        (gamma-1)*E+(3-gamma)/2*rho*u**2,
                        w1eq
                    ]
                },
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': E,
                    'polynomials': [1, X, X**2/2],
                    'relaxation_parameters': [0, symb_s_p, symb_s_px],
                    'equilibrium': [
                        E,
                        gamma*E*u-(gamma-1)/2*rho*u**3,
                        w2eq
                    ]
                },
            ],
            'parameters': {
                la_: la,
                s_rho_: s_rho,
                s_u_: s_u,
                s_p_: s_p,
                s_rhox_: s_rhox,
                s_ux_: s_ux,
                s_px_: s_px,
                sigma_rho: 1/s_rho_-.5,
                sigma_u: 1/s_u_-.5,
                sigma_p: 1/s_p_-.5,
                sigma_rhox: 1/s_rhox_-.5,
                sigma_ux: 1/s_ux_-.5,
                sigma_px: 1/s_px_-.5,
            },
            'generator': 'numpy'
        }

    def get_boundary(self):
        return {
            self.equation.NonReflexiveOutlet: {
                'method': {
                    0: pylbm.bc.Neumann,
                    1: pylbm.bc.Neumann,
                    2: pylbm.bc.Neumann,
                },
            },
            self.equation.Neumann: {
                'method': {
                    0: pylbm.bc.Neumann,
                    1: pylbm.bc.Neumann,
                    2: pylbm.bc.Neumann,
                },
            },
            self.equation.Dirichlet_u: {
                'method': {
                    0: pylbm.bc.BounceBack,
                    1: pylbm.bc.AntiBounceBack,
                    2: pylbm.bc.BounceBack,
                },
            },
        }

class D1Q333(D1Q333_general):
    addvisc = 0.5
    name = 'D1Q333_0'
    tex_name = r'$D_1Q_{{333}}0$'

    def _get_equilibrium(self, rho, q, E, gamma):
        u = q/rho              # velocity
        w0eq = E
        w1eq = (3*E-rho*u**2)*u
        w2eq = 6*E**2/rho-rho*u**4
        return w0eq, w1eq, w2eq


class D1Q333_NS(D1Q333_general):
    addvisc = 0.1
    name = 'D1Q333_1'
    tex_name = r'$D_1Q_{{333}}1$'

    def _get_equilibrium(self, rho, q, E, gamma):
        u = q/rho              # velocity
        Ec = rho*u**2/2        # kinetic energy
        p = (gamma-1)*(E-Ec)   # pressure
        w0eq = Ec + p/2
        w1eq = (Ec + 3/2*p) * u
        coeff = (5*gamma-1)/(gamma-1)
        w2eq = (Ec + coeff/2*p) * u**2/2
        return w0eq, w1eq, w2eq
