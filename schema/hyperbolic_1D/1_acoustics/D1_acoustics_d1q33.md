The D1Q33 scheme is a vectorial scheme
that can be used for the isentropic acoustics equation in dimension one.

---

**Vectorial scheme**

The D1Q33 is a vectorial scheme with one particle distribution function
for each conserved moment (the mass and the momentum).
Each particle distribution function is discretized with three velocities:
$0$, $\lambda$ and $-\lambda$ where $\lambda$ is the lattice velocity.

This scheme has more degress of freedom than the D1Q22: the second-order operator corresponding to the numerical diffusion can be modified by choosing the equilibrium value of the second-order moment. However, the stability zone according to the parameters of the scheme is more complicated.

The scheme is described by the six moments $\rho$, $\phi_\rho$, $\psi_\rho$, $q$, $\phi_q$, and $\psi_q$. 

Denoting $(f_0,f_-,f_+)$ the particle distribution functions associated to the mass, we have

$$
\rho = f_0 + f_- + f_+,
\quad
\phi_\rho = \lambda (-f_- + f_+),
\quad
\psi_\rho = \tfrac{1}{2} \lambda^2 (f_-+f_+).
$$

Denoting $(g_0,g_-,g_+)$ the particle distribution functions associated to the momentum, we have

$$
q = g_0 + g_- + g_+,
\quad
\phi_q = \lambda (-g_- + g_+),
\quad
\psi_q = \tfrac{1}{2} \lambda^2 (g_-+g_+).
$$

The equilibrium value of the non-conserved moments read

$$
\phi_\rho^{\text{eq}} = q,
\qquad
\psi_\rho^{\text{eq}} = \tfrac{1}{2} \alpha \lambda^2\rho,
$$

and

$$
\phi_q^{\text{eq}} = c^2\rho,
\qquad
\psi_q^{\text{eq}} = \tfrac{1}{2} \beta \lambda^2q,
$$

where $\alpha$ and $\beta$ are free real parameters.

---

**Parameters**

Seven parameters are left free:

- the **lattice velocity** denoted by $\lambda$ ;
- the **four relaxation parameters** $s_{\rho}$, $s_{\rho x}$, $s_q$ and $s_{qx}$ ;
- the **two equilibrium parameters** $\alpha$ and $\beta$.

1. _The lattice velocity $\lambda$_

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\lambda$ has to be greater than the physical velocity of the problem $c$;
> - The parameter $\lambda$ should be as small as possible while preserving the stability in order to minimize the numerical diffusion.

2. _The relaxation parameters $s_{\rho}$ and $s_q$_

> The two relaxation parameters are involved in the relaxation towards equilibrium for the two non-conserved moments of the scheme. These parameters should take real values between 0 and 2.
>
> These parameters play also a role in the numerical diffusion: $s_{\rho}$ (_resp._ $s_q$) appears in the numerical diffusion operator of the mass (_resp._ momentum) conservation through the Henon parameter.
>
> - Increasing the values of the parameters $s_{\rho}$ and $s_q$ decreases the numerical diffusion;
> - Decreasing the values improves the stability.

3. _The equilibrium parameters $\alpha$ and $\beta$_

> The two equilibrium parameters $\alpha$ and $\beta$ are involved in the numerical diffusion.
>
> - Decreasing the values of these parameters decreases the numerical diffusion;
> - Increasing the values improves the stability.

---

**How to choose the parameters ?**

Even if the equivalent equations give only an asymptotic representation of the scheme, the structure of the second-order operator (corresponding to a numerical diffusion) is very helpfull for selecting the several parameters.
The complete structure can be computed using the tab `Equivalent equations`. It reads

$$
\left\lbrace\begin{aligned}
    \partial_t \rho + \partial_x q = \Delta t \sigma_\rho (\alpha\lambda^2 - c^2) \partial_{xx} \rho + \mathcal{O}(\Delta t^2),\\
    \partial_t q + c^2 \partial_x \rho = \Delta t \sigma_q (\beta\lambda^2 - c^2) \partial_{xx} q + \mathcal{O}(\Delta t^2).
\end{aligned}\right.
$$

For each relaxation parameter $s \in \lbrace s_{\rho}, s_q \rbrace$ , the Henon parameter is defined by $\sigma = 1/s - 1/2$ and the amplitude of the associated numerical diffusion is given by $\Delta x \lambda\sigma$ , where $\Delta x$ is the space step.

> &rarr; the lattice velocity $\lambda$ has to be large enough to ensure that the second-order operator is positive (in the sense of the parabolic system);
>
> &rarr; the relaxation parameters should be chosen as close to $2$ as possible to minimise the effect of the numerical diffusion.

---

_See the tabs `Linear Stability` and `Parametric Study` for more informations_.
