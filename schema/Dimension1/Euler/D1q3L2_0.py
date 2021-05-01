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
from ...utils import LBM_scheme, RelaxationParameter, RealParameter

class D1Q3L2(LBM_scheme):
    s_rho: RelaxationParameter('s_rho')
    s_u: RelaxationParameter('s_u')
    s_p: RelaxationParameter('s_p')
    alpha: RealParameter('alpha')
    equation = Euler1D()
    dim = 1
    name = 'D1Q3L2'
    tex_name = r'$D_1Q_3L_2$'

    def get_dictionary(self):
        rho = self.equation.rho
        q = self.equation.q
        E = self.equation.E
        gamma = self.equation.gamma

        la_, la = self.la.symb, self.la.value
        s_rho_, s_rho = self.s_rho.symb, self.s_rho.value
        s_u_, s_u = self.s_u.symb, self.s_u.value
        s_p_, s_p = self.s_p.symb, self.s_p.value

        sigma_1 = sp.symbols('sigma_1', constants=True)
        sigma_2 = sp.symbols('sigma_2', constants=True)
        sigma_3 = sp.symbols('sigma_3', constants=True)

        symb_s_1 = 1/(.5+sigma_1)          # symbolic relaxation parameter
        symb_s_2 = 1/(.5+sigma_2)          # symbolic relaxation parameter
        symb_s_3 = 1/(.5+sigma_3)          # symbolic relaxation parameter

        ALPHA_NORM, alpha = self.alpha.symb, self.alpha.value
        ALPHA = ALPHA_NORM * la_**2

        la2 = la_**2
        u = q/rho
        EI = E - q**2/rho/2
        ee = (E/rho-u**2/2) / ALPHA  # p/rho / (gamma-1) / alpha
        p = (gamma-1) * EI

        v = [0, 1, 2, 0, 1, 2]              # velocities
        # self.nv = len(v)
        M = sp.Matrix(
            [
                [1, 1, 1, 1, 1, 1],
                [0, la_, -la_, 0, la_, -la_],
                [
                    0, la2/2, la2/2,
                    ALPHA, la2/2+ALPHA, la2/2+ALPHA
                ],
                [1, 1, 1, -1, -1, -1],
                [0, la_, -la_, 0, -la_, la_],
                [
                    0, la2/2, la2/2,
                    -ALPHA, -la2/2-ALPHA, -la2/2-ALPHA
                ],
            ]
        )
        deltarho = rho*(1-(3-gamma)*ee)
        deltaq = q * (1 + (la_**2-u**2)/ALPHA - 2*gamma*ee)
        # deltaEc = .25*(
        #     (q+deltaq)**2/(rho+deltarho)
        #     - (q-deltaq)**2/(rho-deltarho)
        # )
        # deltaE = deltaEc + p/(gamma-1) * (
        #     .5 - ee
        # )
        deltaE = E + p/(gamma-1) * (2 - (3-gamma)/2*u**2/ALPHA
        )

        return {
            'dim': 1,
            'scheme_velocity': la_,
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
                la_: la,
                ALPHA_NORM: alpha,
                s_rho_: s_rho,
                s_u_: s_u,
                s_p_: s_p,
                sigma_1: 1/s_rho_-.5,
                sigma_2: 1/s_u_-.5,
                sigma_3: 1/s_p_-.5,
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

    @property
    def description(self):
        return """
The D1Q3L2 scheme is a LBM scheme
with two levels of internal energy
that can be used for inviscid flows in dimension one.

---

**Scheme with internal energy levels**

The D1Q3L2 is a scheme with two particle distribution functions, one for each internal energy level. The two internal energy levels are scaled by $\\lambda^2$ ($\\lambda$ is the lattice velocity) and the difference between their values is parametrized by $\\alpha$.

Each particle distribution function is discretized with three velocities:
$0$, $\\lambda$, and $-\\lambda$ where $\\lambda$ is the lattice velocity.

This scheme has exactly the same number of degrees of freedom than the D1Q222 but the second-order operator corresponding to the numerical diffusion is different: its contribution in the mass conservation equation vanishes.

---

**Parameters**

The equilibrium value of all the non-conserved moments are fixed.
Five parameters are left free:

* the **lattice velocity** denoted by $\\lambda$;
* the **three relaxation parameters** $s_{\\rho}$, $s_u$, and $s_p$;
* the **difference between the levels of internal energy** $\\alpha$.

1. *The lattice velocity $\\lambda$*

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\\lambda$ has to be greater than all the physical velocities of the problem;
> - The parameter $\\lambda$ should be as small as possible while preserving the stability;

2. *The relaxation parameters $s_{\\rho}$, $s_u$, and $s_p$*

> These three parameters should take real values between 0 and 2. Two of these three relaxation parameters ($s_u$ and $s_p$) are involved in the relaxation towards equilibrium for the associated non-conserved moments.

3. *The difference of internal energy levels $\\alpha$*

> The parameter $\\alpha$ is involved in the second-order operator (the numerical diffusion), more precisely in the conservation equation of the energy. 

---

**Warning**

Choose the several parameters to ensure the stability of this scheme is not an easy task!

---

*See the tabs `Linear Stability` and `Parametric Study` for more informations*.
        """
