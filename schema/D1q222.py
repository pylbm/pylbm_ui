from pydantic import BaseModel, Field
import sympy as sp
import pylbm
import traitlets
from .equation_type import EquationType, Euler1D
from .utils import Scheme, RelaxationParameter


class D1Q222(BaseModel, Scheme):
    s_rho: RelaxationParameter
    s_u: RelaxationParameter
    s_p: RelaxationParameter
    dx: float
    la: float

    equation = Euler1D()
    dim = 1
    name = 'D1Q222'
    tex_name = r'$D_1Q_{{222}}$'

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        E = self.equation.E
        gamma = self.equation.gamma

        u = q/rho

        self.dx = 0.01
        self.la = 10
        s_rho_ = sp.symbols('s_rho', constants=True)
        s_u_ = sp.symbols('s_u', constants=True)
        s_p_ = sp.symbols('s_p', constants=True)
        sigma_rho = sp.symbols('sigma_rho', constants=True)
        sigma_u = sp.symbols('sigma_u', constants=True)
        sigma_p = sp.symbols('sigma_p', constants=True)

        LA = sp.symbols('lambda', constants=True)
        X = sp.symbols('X')

        return {
            'dim': 1,
            'space_step': self.dx,
            'scheme_velocity': LA,
            'schemes': [
                {
                    'velocities': [1, 2],
                    'conserved_moments': rho,
                    'polynomials': [1, X],
                    'relaxation_parameters': [0, 1/(.5+sigma_rho)],
                    'equilibrium': [rho, q]
                },
                {
                    'velocities': [1, 2],
                    'conserved_moments': q,
                    'polynomials': [1, X],
                    'relaxation_parameters': [0, 1/(.5+sigma_u)],
                    'equilibrium': [q, (gamma-1)*E+(3-gamma)/2*rho*u**2]
                },
                {
                    'velocities': [1, 2],
                    'conserved_moments': E,
                    'polynomials': [1, X],
                    'relaxation_parameters': [0, 1/(.5+sigma_p)],
                    'equilibrium': [E, gamma*E*u-(gamma-1)/2*rho*u**3]
                },
            ],
            'parameters': {
                LA: self.la,
                s_rho_: self.s_rho,
                s_u_: self.s_u,
                s_p_: self.s_p,
                sigma_rho: 1/s_rho_-.5,
                sigma_u: 1/s_u_-.5,
                sigma_p: 1/s_p_-.5,
                gamma: 1.4
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

    @property
    def description(self):
        return """
The $D_1Q_{222}$ scheme is the smallest vectorial scheme for inviscid flows.

It involves the following set of parameters:

Relaxation rates (values must be in $]0,2[$):\n


- $s_{\\rho}$: the relaxation rate for the density equation\n
- $s_u$: the relaxation rate for the velocity equation\n
- $s_p$: the relaxation rate for the pressure equation\n
       """

    def get_default_parameters(self, test_case_name='none', printFlg=False):

        if test_case_name == "Toro_1":
            dx, la = 1/256, 5
            srho, su, sp = 1.9, 1.8, 2.
        elif test_case_name == "Toro_2":
            dx, la = 1/256, 4
            srho, su, sp = 1.7, 1.7, 1.7
        elif test_case_name == "Toro_3":
            dx, la = 1/512, 60
            srho, su, sp = 1.5, 1.5, 1.5
        elif test_case_name == "Toro_4":
            dx, la = 1/2048, 50
            srho, su, sp = 1.8, 1.8, 1.8
        elif test_case_name == "Toro_5":
            dx, la = 1/512, 40
            srho, su, sp = 1.85, 1.8, 1.6
        else:
            dx, la = 1/256, 1
            srho, su, sp = 1, 1, 1

        if printFlg:
            #print("Test case: {}".format(test_case_name))
            print("""Proposition of parameters for selected test case: {}
(!valid for default test case parameters only!)
        dx =        {}
        la =        {}
        s_rho =     {}
        s_u =       {}
        s_p =       {}
        """.format(test_case_name, dx, la, srho, su, sp))

        defParam = {
            'dx': dx,
            'la': la,
            's_rho': srho,
            's_u': su,
            's_p': sp
            }

        return defParam

    def get_S(self):
        return {'s_rho': self.s_rho,
                's_u': self.s_u,
                's_p': self.s_p}
    def get_Disc(self):
        return {'dx': self.dx,
                'la': self.la}
    def get_EquParams(self):
        return {}

