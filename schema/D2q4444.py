from pydantic import BaseModel, Field
import sympy as sp
import pylbm
import traitlets
from .equation_type import EquationType, Euler2D
from .utils import Scheme, RelaxationParameter

from .boundary2D import *


class D2Q4444(BaseModel, Scheme):
    s_rho: RelaxationParameter
    s_u: RelaxationParameter
    s_p: RelaxationParameter
    s_rho2: RelaxationParameter
    s_u2: RelaxationParameter
    s_p2: RelaxationParameter
    la: float

    equation = Euler2D()
    dim = 2
    name = 'D2Q4444'
    tex_name = r'$D_2Q_{{4444}}$'

    def get_dictionary(self):
        rho = self.equation.rho
        qx = self.equation.qx
        qy = self.equation.qy
        E = self.equation.E
        gamma = self.equation.gamma

        ux = qx/rho
        uy = qy/rho
        EpP = gamma*E - (gamma-1)*rho/2*(ux**2+uy**2)

        s_rho_ = sp.symbols('s_rho', constants=True)
        s_u_ = sp.symbols('s_u', constants=True)
        s_p_ = sp.symbols('s_p', constants=True)
        s_rho2_ = sp.symbols('s_rho2', constants=True)
        s_u2_ = sp.symbols('s_u2', constants=True)
        s_p2_ = sp.symbols('s_p2', constants=True)
        sigma_rho = sp.symbols('sigma_rho', constants=True)
        sigma_u = sp.symbols('sigma_u', constants=True)
        sigma_p = sp.symbols('sigma_p', constants=True)
        sigma_rho2 = sp.symbols('sigma_rho2', constants=True)
        sigma_u2 = sp.symbols('sigma_u2', constants=True)
        sigma_p2 = sp.symbols('sigma_p2', constants=True)

        LA = sp.symbols('lambda', constants=True)
        X = sp.symbols('X')
        Y = sp.symbols('Y')

        return {
            'dim': self.dim,
            'scheme_velocity': LA,
            'schemes': [
                {
                    'velocities': list(range(1, 5)),
                    'conserved_moments': rho,
                    'polynomials': [1, X, Y, X**2-Y**2],
                    'relaxation_parameters': [0, 1/(.5+sigma_rho), 1/(.5+sigma_rho), 1/(.5+sigma_rho2)],
                    'equilibrium': [rho,
                                    qx,
                                    qy,
                                    rho*(ux**2-uy**2)]
                },
                {
                    'velocities': list(range(1, 5)),
                    'conserved_moments': qx,
                    'polynomials': [1, X, Y, X**2-Y**2],
                    'relaxation_parameters': [0, 1/(.5+sigma_u), 1/(.5+sigma_u), 1/(.5+sigma_u2)],
                    'equilibrium': [qx,
                                    (gamma-1)*E+rho/2*((3-gamma)*ux**2+(1-gamma)*uy**2),
                                    qx*uy,
                                    0.]
                                    #qx*(ux**2-uy**2)]
                },
                {
                    'velocities': list(range(1, 5)),
                    'conserved_moments': qy,
                    'polynomials': [1, X, Y, X**2-Y**2],
                    'relaxation_parameters': [0, 1/(.5+sigma_u), 1/(.5+sigma_u), 1/(.5+sigma_u2)],
                    'equilibrium': [qy,
                                    qx*uy,
                                    (gamma-1)*E+rho/2*((3-gamma)*uy**2+(1-gamma)*ux**2),
                                    0.]
                                    #qy*(ux**2-uy**2)]
                },
                {
                    'velocities': list(range(1, 5)),
                    'conserved_moments': E,
                    'polynomials': [1, X, Y, X**2-Y**2],
                    'relaxation_parameters': [0, 1/(.5+sigma_p), 1/(.5+sigma_p), 1/(.5+sigma_p2)],
                    'equilibrium': [E,
                                    EpP*ux,
                                    EpP*uy,
                                    0.]
                                    #E*(ux**2-uy**2)]
                },
            ],
            'parameters': {
                LA: self.la,
                s_rho_: self.s_rho,
                s_u_: self.s_u,
                s_p_: self.s_p,
                s_rho2_: self.s_rho2,
                s_u2_: self.s_u2,
                s_p2_: self.s_p2,
                sigma_rho: 1/s_rho_-.5,
                sigma_u: 1/s_u_-.5,
                sigma_p: 1/s_p_-.5,
                sigma_rho2: 1/s_rho2_-.5,
                sigma_u2: 1/s_u2_-.5,
                sigma_p2: 1/s_p2_-.5,
                gamma: 1.4
            },
            'generator': 'cython'
        }

    def get_boundary(self):
        return {
            self.equation.NonReflexiveOutlet: {
                'method': {
                    0: pylbm.bc.Neumann,
                    1: pylbm.bc.Neumann,
                    2: pylbm.bc.Neumann,
                    3: pylbm.bc.Neumann,
                },
            },
            self.equation.Neumann: {
                'method': {
                    0: pylbm.bc.Neumann,
                    1: pylbm.bc.Neumann,
                    2: pylbm.bc.Neumann,
                    3: pylbm.bc.Neumann,
                },
            },
            self.equation.Dirichlet_u: {
                'method': {
                    0: pylbm.bc.BounceBack,
                    1: pylbm.bc.AntiBounceBack,
                    2: pylbm.bc.AntiBounceBack,
                    3: pylbm.bc.BounceBack,
                },
            },
            self.equation.Symmetry_X:{
                'method':{
                    0: pylbm.bc.BounceBack,
                    1: SlipXEven,
                    2: pylbm.bc.AntiBounceBack,
                    3: pylbm.bc.BounceBack
                },
            },
            self.equation.Symmetry_Y:{
                'method':{
                    0: pylbm.bc.BounceBack,
                    1: pylbm.bc.AntiBounceBack,
                    2: SlipYEven,
                    3: pylbm.bc.BounceBack
                },
            }
        }

    @property
    def description(self):
        return """
The $D_2Q_{4444}$ scheme is the smallest vectorial scheme for inviscid flows.

It involves the following set of parameters:
in theory the scheme involves 12 relaxation parameters. Isotropy consideration allows to reduce this number to 6

Relaxation rates (values must be in $]0,2[$):

- $s_{\\rho}$: the relaxation rate for the density equation
- $s_{u}$: the relaxation rate for the velocity equation !!!!!!!-> changer pour equation de moment (dans les faits)
- $s_{p}$: the relaxation rate for the pressure equation !!!!!!!-> changer pour equation d'Energie (dans les faits)
- $s_{\\rho^2}$: the relaxation rate for the density equation
- $s_{u^2}$: the relaxation rate for the velocity equation
- $s_{p^2}$: the relaxation rate for the pressure equation
       """
