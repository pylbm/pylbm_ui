# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
# from pydantic import BaseModel, Field
import sympy as sp
import pylbm
import traitlets
from .equation_type import Transport1D
from ...utils import LBM_scheme, RelaxationParameter


class D1Q2(LBM_scheme):
    s_u: RelaxationParameter('s_u')

    equation = Transport1D()
    dim = 1
    name = 'D1Q2'
    tex_name = r'$D_1Q_{{2}}$'

    def get_required_param(self):
        return [self.equation.c]

    def get_dictionary(self):
        u = self.equation.u
        c = self.equation.c

        la_, la = self.la.symb, self.la.value
        s_u_, s_u = self.s_u.symb, self.s_u.value
        sigma_u = sp.symbols('sigma_u', constants=True)

        X = sp.symbols('X')

        return {
            'dim': 1,
            'scheme_velocity': la_,
            'schemes': [
                {
                    'velocities': [1, 2],
                    'conserved_moments': u,
                    'polynomials': [1, X],
                    'relaxation_parameters': [0, 1/(.5+sigma_u)],
                    'equilibrium': [u, c*u]
                },
            ],
            'parameters': {
                la_: la,
                s_u_: s_u,
                sigma_u: 1/s_u_-.5,
                
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
                    # 1: pylbm.bc.AntiBounceBack,
                    # 2: pylbm.bc.BounceBack,
                },
            },
        }

    @property
    def description(self):
        return """
The D1Q2 scheme is the smallest scheme
that can be used for the advection equation in dimension one.

---

**The simplest scheme**

The D1Q2 is a scheme with one particle distribution function 
discretized with two velocities:
$\lambda$ and $-\lambda$ where $\lambda$ is the lattice velocity.

The main interest of this scheme is its simplicity.
This scheme is very rough and robust. However, the structure of the numerical diffusion cannot be modified.

---

**Parameters**

Only two parameters are left free:

* the **lattice velocity** denoted by $\lambda$;
* the **relaxation parameter** $s$.

1. *The lattice velocity $\lambda$*

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\lambda$ has to be greater than all the physical velocities of the problem;
> - The parameter $\lambda$ should be as small as possible while preserving the stability.

2. *The relaxation parameter $s$*

> The relaxation parameter is involved in the relaxation towards equilibrium for the non-conserved moment of the scheme. This parameter should take a real value between $0$ and $2$.
>
> This parameter plays also a role in the numerical diffusion through the Henon parameter denoted by $\sigma=1/s-1/2$.
>
> - Increasing the value of the parameters $s$ decreases the numerical diffusion;
> - Decreasing the value improves the stability.

---

The D1Q2 can be used to simulate the advection equation as its second-order equivalent equation (*See the tab `Equivalent equations` for more details*) reads

$$
    \partial_t u + c \partial_x u = \Delta t \sigma (\lambda^2 - c^2) \partial_{xx} u + \mathcal{O}(\Delta t^2).
$$

where $\Delta t$ is the time step of the scheme.

For this very simple scheme, we obtain through the second-order operator the following properties :
> 1. the lattice velocity $\lambda$ must satisfy $\lambda \geq |c|$;
> 2. the numerical diffusion is driven by the coefficient $\lambda\sigma(\lambda^2-c^2)$.

---

*See the tabs `Linear Stability` and `Parametric Study` for more informations*.
       """
