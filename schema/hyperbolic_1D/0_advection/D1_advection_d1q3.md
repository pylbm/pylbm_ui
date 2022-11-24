The D1Q3 scheme is a scheme
that can be used for the advection equation in dimension one.

---

**The 3-velocities scheme**

The D1Q3 is a scheme with one particle distribution function
discretized with three velocities: $0$,
$\lambda$, and $-\lambda$ where $\lambda$ is the lattice velocity.

This scheme has more degrees of freedom than the D1Q2: the second-order operator corresponding to the numerical diffusion can be modified by choosing the equilibrium value of the second-order moment. However, the stability zone according to the parameters of the scheme is more complicated.

The scheme is described by the three moments $u$, $v$, and $w$ 

$$
u = f_0 + f_- + f_+,
\quad
v = \lambda (-f_- + f_+),
\quad
w = \tfrac{1}{2} \lambda^2 (f_-+f_+),
$$

where $f_0$, $f_-$, and $f_+$ are the distribution particle functions with velocity $0$, $-\lambda$, and $\lambda$.

The equilibrium value of the non-conserved moments read

$$
v^{\text{eq}} = c u,
\qquad
w^{\text{eq}} = \tfrac{1}{2} T \lambda^2u,
$$

where $T$ is a free real parameter.

---

**Parameters**

Four parameters are left free:

- `lambda`: the **lattice velocity** denoted by $\lambda$;
- `s_u` and `s_ux`: the two **relaxation parameters** $s_u$ and $s_{ux}$;
- `T`: the parameter $T$ used to fix the equilibrium of the second-order moment denoted by $T$;

1. _The lattice velocity $\lambda$_

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\lambda$ has to be greater than all the physical velocities of the problem;
> - The parameter $\lambda$ should be as small as possible while preserving the stability.

2. _The relaxation parameter $s_u$_

> This relaxation parameter is involved in the relaxation towards equilibrium for the first-order non-conserved moment of the scheme $v$. This parameter should take a real value between $0$ and $2$.
>
> This parameter plays also a role in the numerical diffusion through the Henon parameter denoted by $\sigma_u=1/{s_u}-1/2$.
>
> - Increasing the value of the parameters $s_u$ decreases the numerical diffusion;
> - Decreasing the value improves the stability.

3. _The relaxation parameter $s_{ux}$_

> This relaxation parameter is involved in the relaxation towards equilibrium for the second-order non-conserved moment of the scheme $w$. This parameter should take a real value between $0$ and $2$.
>
> This parameter does not play a role in the second-order numerical diffusion but in the stability. A good choice is often to take $s_{ux}=s_u$ (Single-Relaxation-Time scheme).

4. _The equilibrium parameter $T$_

> The parameter $T$ is used to fix the equilibrium of the second-order moment $w^{\text{eq}} = \tfrac{1}{2} T \lambda^2u$. The second-order numerical diffusion being proportional to $T\lambda^2-c^2$, the choice $T=(c/\lambda)^2$ could be a nice choice but involves often instabilities.
>
> **Remark**: the choice $T=1$ yields to a particular simplification of the $D1Q3$ that reduces exactly to the corresponding $D1Q2$. The second-order moment $w$ plays in that case the role of a slave.

---

The D1Q3 can be used to simulate the advection equation as its second-order equivalent equation (_See the tab `Equivalent equations` for more details_) reads

$$
    \partial_t u + c \partial_x u = \Delta t \sigma (T\lambda^2 - c^2) \partial_{xx} u + \mathcal{O}(\Delta t^2).
$$

where $\Delta t$ is the time step of the scheme.

For this scheme, we obtain through the second-order operator the following properties :

> 1. the lattice velocity $\lambda$ and the parameter $T$ must satisfy $T\lambda^2\geq c^2$;
> 2. the numerical diffusion is driven by the coefficient $\lambda\sigma(T\lambda^2-c^2)$.

---

_See the tabs `Linear Stability` and `Parametric Study` for more informations_.
