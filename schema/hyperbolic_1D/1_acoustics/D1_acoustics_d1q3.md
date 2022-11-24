The D1Q3 scheme is the smallest scheme
that can be used for the isentropic acoustics equation in dimension one.

---

**The 3-velocities scheme**

The D1Q3 is a scheme with one particle distribution function
discretized with three velocities: $0$,
$\lambda$, and $-\lambda$ where $\lambda$ is the lattice velocity.

The scheme is described by the three moments $\rho$, $q$, and $E$. The two first moments are conserved while the third one relaxes toward an equilibrium value $E^{\text{eq}}$ according to a relaxation parameter denoted by $s$.

$$
\rho = f_0 + f_- + f_+,
\quad
q = \lambda (-f_- + f_+),
\quad
E = \lambda^2 (f_-+f_+),
$$

where $f_0$, $f_-$, and $f_+$ are the distribution particle functions with velocity $0$, $-\lambda$, and $\lambda$. Note that the moment $E$ differs from the energy of the system by a factor one half (just to not multiply and divide by 2 at each iteration!).

The equilibrium value of the non-conserved moment reads

$$
E^{\text{eq}} = c^2 \rho,
$$

in order to be consistent with the PDE's system. So the structure of the numerical diffusion cannot be modified.

---

**Parameters**

Two parameters are left free:

- the **lattice velocity** denoted by $\lambda$ ;
- the **relaxation parameter** $s$ .

1. _The lattice velocity $\lambda$_

> The lattice velocity is defined as the ratio between the space step and the time step. This velocity must satisfy a CFL type condition to ensure the stability of the scheme.
>
> This parameter is involved in the numerical diffusion: the higher the lattice velocity, the higher the numerical diffusion.
>
> - The parameter $\lambda$ has to be greater than the physical velocity of the problem $c$;
> - The parameter $\lambda$ should be as small as possible while preserving the stability in order to minimize the numerical diffusion.

2. _The relaxation parameter $s$_

> The relaxation parameter is involved in the relaxation towards equilibrium for the non-conserved moment of the scheme. This parameter should take real values between 0 and 2.
>
> This parameter plays also a role in the numerical diffusion: $s$ appears in the numerical diffusion operator of the momentum conservation through the Henon parameter.
>
> - Increasing the values of the parameters $s$ decreases the numerical diffusion;
> - Decreasing the values improves the stability.

---

**How to choose the parameters ?**

Even if the equivalent equations give only an asymptotic representation of the scheme, the structure of the second-order operator (corresponding to a numerical diffusion) is very helpfull for selecting the several parameters.
The complete structure can be computed using the tab `Equivalent equations`. It reads

$$
\left\lbrace\begin{aligned}
    &\partial_t \rho + \partial_x q = \mathcal{O}(\Delta t^2),\\
    &\partial_t q + c^2 \partial_x \rho = \Delta t \sigma (\lambda^2 - c^2) \partial_{xx} q + \mathcal{O}(\Delta t^2).
\end{aligned}\right.
$$

The Henon parameter is defined by $\sigma = 1/s - 1/2$ and the amplitude of the associated numerical diffusion is given by $\Delta x \lambda\sigma$ , where $\Delta x$ is the space step.

> &rarr; the lattice velocity $\lambda$ has to be large enough to ensure that the second-order operator is positive (in the sense of the parabolic system);
>
> &rarr; the relaxation parameters should be chosen as close to $2$ as possible to minimise the effect of the numerical diffusion.

---

_See the tabs `Linear Stability` and `Parametric Study` for more informations_.
