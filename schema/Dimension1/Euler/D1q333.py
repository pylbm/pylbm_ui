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

    @property
    def description(self):
        return """
The D1Q333 scheme is a vectorial scheme
that can be used for inviscid flows in dimension one.

---

**Vectorial scheme**

The D1Q333 is a vectorial scheme with one particle distribution function
for each conserved moment (the mass, the momentum, and the total energy).
Each particle distribution function is discretized with three velocities:
$0$, $\lambda$, and $-\lambda$ where $\lambda$ is the lattice velocity.

This scheme has more degrees of freedom than the D1Q222: the second-order operator corresponding to the numerical diffusion can be modified by choosing the equilibrium value of the second-order moments. However, the stability zone according to the parameters of the scheme is not easy to determine.

Two versions of this scheme are proposed: the D1Q333_0 and the D1Q333_1 that differ in their equilibrium values for the second-order moments.

---

**Parameters**

The equilibrium value of all the non-conserved moments are fixed in this version of the D1Q333. 
Seven parameters are left free:

* the **lattice velocity** denoted by $\lambda$;
* the **three relaxation parameters of first-order** $s_{\\rho}$ , $s_u$ , and $s_p$ ;
* the **three relaxation parameters of second-order** $s_{\\rho x}$ , $s_{ux}$ , and $s_{px}$ .

1. *The lattice velocity $\lambda$*

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\lambda$ has to be greater than all the physical velocities of the problem;
> - The parameter $\lambda$ should be as small as possible while preserving the stability.

2. *The relaxation parameters of first-order $s_{\\rho}$ , $s_u$ , and $s_p$*

> These three relaxation parameters are involved in the relaxation towards equilibrium for the three first-order non-conserved moments of the scheme. These parameters should take real values between $0$ and $2$.
>
> These parameters play also a role in the numerical diffusion: $s_{\\rho}$ (*resp.* $s_u$ , $s_p$) appears in the numerical diffusion operator of the mass (*resp.* momentum, energy) conservation through the Henon parameter.
>
> - Increasing the values of the parameters $s_{\\rho}$ , $s_u$ , and $s_p$ decreases the numerical diffusion;
> - Decreasing the values improves the stability.

3. *The relaxation parameters of second-order $s_{\\rho x}$ , $s_{ux}$ , and $s_{px}$*

> These three relaxation parameters are involved in the relaxation towards equilibrium for the three second-order non-conserved moments of the scheme. These parameters should take real values between $0$ and $2$.
>
> These parameters do not play a role in the second-order numerical diffusion but in the stability. A good choice is often to take these three parameters equal to 1 except when the pressure can be closed to 0.

---

**How to choose the parameters ?**

Even if the equivalent equations give only an asymptotic representation of the scheme, the structure of the second-order operator (corresponding to a numerical diffusion) is very helpfull for selecting the several parameters.
The complete structure can be computed using the tab `Equivalent equations`.

For each relaxation parameter $s \in \lbrace s_{\\rho}, s_u, s_p \\rbrace$ , the Henon parameter is defined by $\sigma = 1/s - 1/2$ and the amplitude of the associated numerical diffusion is given by $\Delta x \lambda\sigma$ , where $\Delta x$ is the space step.

> &rarr; the lattice velocity $\lambda$ has to be large enough to ensure that the second-order operator is positive (in the sense of the parabolic system);
>
> &rarr; the relaxation parameters of first-order should be chosen as close to $2$ as possible to minimise the effect of the numerical diffusion;
>
> &rarr; the relaxation parameters of second-order do not play a role in the numerical diffusion: a good compromise is to choose a value close to $1$.

---

*See the tabs `Linear Stability` and `Parametric Study` for more informations*.        
        """


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