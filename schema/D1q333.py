from pydantic import BaseModel
import sympy as sp
import pylbm
from .equation_type import Euler1D
from .utils import Scheme, RelaxationParameter

class D1Q333(BaseModel, Scheme):
    s_rho: RelaxationParameter
    s_u: RelaxationParameter
    s_p: RelaxationParameter
    s_rhox: RelaxationParameter
    s_ux: RelaxationParameter
    s_px: RelaxationParameter
    dx: float
    la: float

    equation = Euler1D()
    dim = 1
    name = 'D1Q333'
    tex_name = r'$D_1Q_{{333}}$'

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        E = self.equation.E
        gamma = self.equation.gamma

        u = q/rho

        sigma_rho = sp.symbols('sigma_rho', constants=True)
        sigma_u = sp.symbols('sigma_u', constants=True)
        sigma_p = sp.symbols('sigma_p', constants=True)
        sigma_rhox = sp.symbols('sigma_rhox', constants=True)
        sigma_ux = sp.symbols('sigma_ux', constants=True)
        sigma_px = sp.symbols('sigma_px', constants=True)

        s_rho = sp.symbols('s_rho', constants=True)
        s_u = sp.symbols('s_u', constants=True)
        s_p = sp.symbols('s_p', constants=True)
        s_rhox = sp.symbols('s_rhox', constants=True)
        s_ux = sp.symbols('s_ux', constants=True)
        s_px = sp.symbols('s_px', constants=True)

        symb_s_rho = 1/(.5+sigma_rho)      # symbolic relaxation parameter
        symb_s_u = 1/(.5+sigma_u)          # symbolic relaxation parameter
        symb_s_p = 1/(.5+sigma_p)          # symbolic relaxation parameter
        symb_s_rhox = 1/(.5+sigma_rhox)    # symbolic relaxation parameter
        symb_s_ux = 1/(.5+sigma_ux)        # symbolic relaxation parameter
        symb_s_px = 1/(.5+sigma_px)        # symbolic relaxation parameter

        LA = sp.symbols('lambda', constants=True)
        X = sp.symbols('X')

        d_rho, d_u, d_p = .5, .5, .5

        return {
            'dim': 1,
            'space_step': self.dx,
            'scheme_velocity': LA,
            'schemes': [
                {
                    'velocities': [0, 1, 2],
                    'conserved_moments': rho,
                    'polynomials': [1, X, X**2/2],
                    'relaxation_parameters': [0, symb_s_rho, symb_s_rhox],
                    'equilibrium': [
                        rho,
                        q,
                        d_rho * LA**2/2*rho + (1-d_rho) * E
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
                        d_u * LA**2/2*q + (1-d_u) * (3*E-rho*u**2)*u
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
                        d_p * LA**2/2*E + (1-d_p)*(6*E**2/rho-rho*u**4)
                    ]
                },
            ],
            'parameters': {
                LA: self.la,
                s_rho: self.s_rho,
                s_u: self.s_u,
                s_p: self.s_p,
                s_rhox: self.s_rhox,
                s_ux: self.s_ux,
                s_px: self.s_px,
                sigma_rho: 1/s_rho-.5,
                sigma_u: 1/s_u-.5,
                sigma_p: 1/s_p-.5,
                sigma_rhox: 1/s_rhox-.5,
                sigma_ux: 1/s_ux-.5,
                sigma_px: 1/s_px-.5,
                gamma: 1.4,
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
The $D_1Q_{333} scheme involves the following set of parameters:

Relaxation rates (values must be in $]0,2[$):

- $s_{\\rho}$: the relaxation rate for the density equation
- $s_{u}$: the relaxation rate for the velocity equation
- $s_{p}$: the relaxation rate for the pressure equation
- $s_{\\rho x}$: the relaxation rate for second order moment? the density equation
- $s_{u x}$: the relaxation rate for the velocity equation
- $s_{p x}$: the relaxation rate for the pressure equation
"""

    def get_default_parameters(self, test_case_name='none', printFlg=False):
        if test_case_name == "Toro_1":
            dx, la = 1/256, 10
            srho, su, sp = 1.9, 1.9, 1.9
            srhox, sux, spx = 1.75, 1.75, 1.75
        elif test_case_name == "Toro_2":
            dx, la = 1/256, 10
            srho, su, sp = 1.95, 1.95, 1.95
            srhox, sux, spx = 1.75, 1.5, 1.75
        elif test_case_name == "Toro_3":
            dx, la = 1/512, 250
            srho, su, sp = 1.9, 1.9, 1.9
            srhox, sux, spx = 1.5, 1.5, 1.5
        elif test_case_name == "Toro_4":
            dx, la = 1/2048, 100
            srho, su, sp = 1.8, 1.8, 1.8
            srhox, sux, spx = 1.5, 1.5, 1.5
        elif test_case_name == "Toro_5":
            dx, la = 1/512, 100
            srho, su, sp = 1.9, 1.8, 1.8
            srhox, sux, spx = 1.8, 1.8, 1.8
        else:
            dx, la = 1/256, 1
            srho, su, sp = 1, 1, 1
            srhox, sux, spx = 1., 1., 1.

        if printFlg:
            #print("Test case: {}".format(test_case_name))
            print("""Proposition of parameters for selected test case: {}
(!valid for default test case parameters only!)
    dx =        {}
    la =        {}
    s_rho =     {}
    s_u =       {}
    s_p =       {}
    s_rhox =    {}
    s_ux =      {}
    s_px =      {}
       """.format(test_case_name, dx, la, srho, su, sp, srhox, sux, spx))

        defParam = {
            'dx': dx,
            'la': la,
            's_rho': srho,
            's_u': su,
            's_p': sp,
            's_rhox': srhox,
            's_ux': sux,
            's_px': spx
            }

        return defParam

    def get_S(self):
        return {'s_rho': self.s_rho,
                's_u': self.s_u,
                's_p': self.s_p,
                's_rhox': self.s_rhox,
                's_ux': self.s_ux,
                's_px': self.s_px}
    def get_Disc(self):
        return {'dx': self.dx,
                'la': self.la}
    def get_EquParams(self):
        return {}




