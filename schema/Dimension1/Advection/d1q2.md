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

- the **lattice velocity** denoted by $\lambda$;
- the **relaxation parameter** $s$.

1. _The lattice velocity $\lambda$_

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\lambda$ has to be greater than all the physical velocities of the problem;
> - The parameter $\lambda$ should be as small as possible while preserving the stability.

2. _The relaxation parameter $s$_

> The relaxation parameter is involved in the relaxation towards equilibrium for the non-conserved moment of the scheme. This parameter should take a real value between $0$ and $2$.
>
> This parameter plays also a role in the numerical diffusion through the Henon parameter denoted by $\sigma=1/s-1/2$.
>
> - Increasing the value of the parameters $s$ decreases the numerical diffusion;
> - Decreasing the value improves the stability.

---

The D1Q2 can be used to simulate the advection equation as its second-order equivalent equation (_See the tab `Equivalent equations` for more details_) reads

$$
    \partial_t u + c \partial_x u = \Delta t \sigma (\lambda^2 - c^2) \partial_{xx} u + \mathcal{O}(\Delta t^2).
$$

where $\Delta t$ is the time step of the scheme.

For this very simple scheme, we obtain through the second-order operator the following properties :

> 1. the lattice velocity $\lambda$ must satisfy $\lambda \geq |c|$;
> 2. the numerical diffusion is driven by the coefficient $\lambda\sigma(\lambda^2-c^2)$.

---

_See the tabs `Linear Stability` and `Parametric Study` for more informations_.
