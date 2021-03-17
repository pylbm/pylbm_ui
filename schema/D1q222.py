from pydantic import BaseModel, Field
import sympy as sp
import pylbm
import traitlets
from .equation_type import EquationType, Euler1D
from .utils import LBM_scheme, RelaxationParameter

class D1Q222(LBM_scheme):
    s_rho: RelaxationParameter('s_rho')
    s_u: RelaxationParameter('s_u')
    s_p: RelaxationParameter('s_p')

    equation = Euler1D()
    dim = 1
    name = 'D1Q222'
    tex_name = r'$D_1Q_{{222}}$'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        E = self.equation.E
        gamma = self.equation.gamma

        u = q/rho

        la_, la = self.la.symb, self.la.value
        s_rho_, s_rho = self.s_rho.symb, self.s_rho.value
        s_u_, s_u = self.s_u.symb, self.s_u.value
        s_p_, s_p = self.s_p.symb, self.s_p.value

        sigma_rho = sp.symbols('sigma_rho', constants=True)
        sigma_u = sp.symbols('sigma_u', constants=True)
        sigma_p = sp.symbols('sigma_p', constants=True)

        # LA = sp.symbols('lambda_', constants=True)
        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
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
                la_: la,
                s_rho_: s_rho,
                s_u_: s_u,
                s_p_: s_p,
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