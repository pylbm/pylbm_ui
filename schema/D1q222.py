# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
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
The D1Q222 scheme is the smallest vectorial scheme
for inviscid flows in dimension one.

---

**Vectorial scheme**

The D1Q222 is a vectorial scheme with one particle distribution function
for each conserved moment (the mass, the momentum, and the total energy).
Each particle distribution function is discretized with two velocities:
$\\lambda$ and $-\\lambda$ where $\\lambda$ is the lattice velocity.

The main interest of this scheme is its simplicity.
This scheme is very rough and robust. However, the structure of the numerical diffusion cannot be modified to fit the physical diffusion operator of Navier-Stokes.

---

**Parameters**

Four parameters are left free:

* the **lattice velocity** denoted by $\\lambda$;
* the **three relaxation parameters** $s_{\\rho}$, $s_u$, and $s_p$.

1. *The lattice velocity $\\lambda$*

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\\lambda$ has to be greater than all the physical velocities of the problem;
> - The parameter $\\lambda$ should be as small as possible while preserving the stability;

2. *The relaxation parameters $s_{\\rho}$, $s_u$, and $s_p$*

> The three relaxation parameters are involved in the relaxation towards equilibrium for the three non-conserved moments of the scheme. These parameters should take real values between 0 and 2.
>
> These parameters play also a role in the numerical diffusion: $s_{\\rho}$ (*resp.* $s_u$, $s_p$) appears in the numerical diffusion operator of the mass (*resp.* momentum, energy) conservation through the Henon parameter.
>
> - Increasing the values of the parameters $s_{\\rho}$, $s_u$, and $s_p$ decreases the numerical diffusion;
> - Decreasing the values improves the stability.

---

*See the tabs `Linear Stability` and `Parametric Study` for more informations*.
       """
