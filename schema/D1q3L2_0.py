from pydantic import BaseModel
import sympy as sp
import pylbm
from .equation_type import EquationType, Euler1D
from .utils import Scheme, RelaxationParameter


class D1Q3L2(BaseModel, Scheme):
    s_rho: RelaxationParameter 
    s_u: RelaxationParameter 
    s_p: RelaxationParameter
    alpha: float 
    dx: float 
    la: float 
    equation = Euler1D()
    dim = 1
    name = 'D1Q3L2'
    tex_name = r'$D_1Q_3L_2$'

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        E = self.equation.E
        gamma = self.equation.gamma

        sigma_1 = sp.symbols('sigma_1', constants=True)
        sigma_2 = sp.symbols('sigma_2', constants=True)
        sigma_3 = sp.symbols('sigma_3', constants=True)

        s1_ = sp.symbols('s_rho', constants=True)
        s2_ = sp.symbols('s_u', constants=True)
        s3_ = sp.symbols('s_p', constants=True)

        symb_s_1 = 1/(.5+sigma_1)          # symbolic relaxation parameter
        symb_s_2 = 1/(.5+sigma_2)          # symbolic relaxation parameter
        symb_s_3 = 1/(.5+sigma_3)          # symbolic relaxation parameter

        LA = sp.symbols('lambda', constants=True)
        ALPHA = sp.symbols('alpha', constants=True)

        LA2 = LA**2
        u = q/rho
        EI = E - q**2/rho/2
        ee = (E/rho-u**2/2) / ALPHA  # p/rho / (gamma-1) / alpha
        p = (gamma-1) * EI

        v = [0, 1, 2, 0, 1, 2]              # velocities
        # self.nv = len(v)
        M = sp.Matrix(
            [
                [1, 1, 1, 1, 1, 1],
                [0, LA, -LA, 0, LA, -LA],
                [
                    0, LA2/2, LA2/2,
                    ALPHA, LA2/2+ALPHA, LA2/2+ALPHA
                ],
                [1, 1, 1, -1, -1, -1],
                [0, LA, -LA, 0, -LA, LA],
                [
                    0, LA2/2, LA2/2,
                    -ALPHA, -LA2/2-ALPHA, -LA2/2-ALPHA
                ],
            ]
        )
        deltarho = rho*(1-(3-gamma)*ee)
        deltaq = q * (1 + (LA**2-u**2)/ALPHA - 2*gamma*ee)
        # deltaEc = .25*(
        #     (q+deltaq)**2/(rho+deltarho)
        #     - (q-deltaq)**2/(rho-deltarho)
        # )
        # deltaE = deltaEc + p/(gamma-1) * (
        #     .5 - ee
        # )
        deltaE = E + p/(gamma-1) * (
            2 - (3-gamma)/2*u**2/ALPHA
        )

        return {
            'dim': 1,
            'space_step': self.dx,
            'scheme_velocity': LA,
            'schemes': [
                {
                    'velocities': v,
                    'conserved_moments': [rho, q, E],
                    'M': M,
                    'relaxation_parameters': [
                        0, 0, 0,
                        symb_s_1, symb_s_2, symb_s_3
                    ],
                    'equilibrium': [
                        rho, q, E,
                        deltarho, deltaq, deltaE
                    ]
                },
            ],
            'parameters': {
                LA: self.la,
                ALPHA: self.alpha,
                s1_: self.s_rho,
                s2_: self.s_u,
                s3_: self.s_p,
                sigma_1: 1/s1_-.5,
                sigma_2: 1/s2_-.5,
                sigma_3: 1/s3_-.5,
                gamma: 1.4,
            },
            'generator': 'numpy'
        }

    def get_boundary(self):
        return {
            self.equation.NonReflexiveOutlet: {
                'method': {
                    0: pylbm.bc.Neumann,
                },
            },
            self.equation.Neumann: {
                'method': {
                    0: pylbm.bc.Neumann,
                },
            },
            self.equation.Dirichlet_u: {
                'method': {
                    0: pylbm.bc.BounceBack,
                },
            },
        }

    def print_description(self):
        print("""The scheme involves the following set of parameters:

    Relaxation rates (values must be in ]0,2[):
        s_rho: the relaxation rate for the density equation  
        s_u: the relaxation rate for the velocity equation 
        s_p: the relaxation rate for the pressure equation 
    Other:
        alpha: ???
       """)

    def get_default_parameters(self, test_case_name='none', printFlg=False):
        alpha = 0.125
        if test_case_name == "Toro_1":
            dx, la = 1/256, 5
            srho, su, sp = 1.5, 1.5, 1.5
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
    dx =              {}
    la = {}
    alpha =           {}
    s_rho =           {}
    s_u =             {}
    s_p =             {}
       """.format(test_case_name, dx, la, alpha, srho, su, sp))
            
        defParam = {
            'dx': dx, 
            'la': la,
            's_rho': srho,
            's_u': su,
            's_p': sp,
            'alpha': alpha
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
        return {'alpha': self.alpha} 
