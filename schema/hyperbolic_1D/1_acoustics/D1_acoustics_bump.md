For this test case, the density $\rho$ and the momentum $q$ are taken as bump functions at the initial time according to

$$
q_0(x) = u_0 \rho_0(x),
$$

where $u_0$ is a constant velocity that can be fixed with the parameter `u_zero`.

The solution reads

$$
\begin{aligned}
\rho(t, x) &= \frac{1}{2}\Bigl(1+\frac{u_0}{c}\Bigr) \rho_0(x-ct) + \frac{1}{2}\Bigl(1-\frac{u_0}{c}\Bigr) \rho_0(x+ct),\\
q(t, x) &= \frac{1}{2}\Bigl(u_0+c\Bigr) \rho_0(x-ct) + \frac{1}{2}\Bigl(u_0-c\Bigr) \rho_0(x+ct).
\end{aligned}
$$

A **bump** function is both smooth (in the sense of having continuous derivatives of all orders) and compactly supported.
In order to investigate the behaviour of the schemes, we also consider **indicator** function of an intervalle or intermadiate regularization of it.
These functions are all compactly supported and their regularity can be chosen with the parameter `reg`.

**Regular bump functions**

The bump functions we consider are piecewise polynomial functions.
The notations are the following:

- `reg` is the number of continuous derivatives of the fields $u$ (denoted by $n$);
- `rho_ground` is the ground value of the fields $\rho$ (denoted by $u_g$);
- `rho_bump` is the top value on the bump (denoted by $\rho_b$);
- `u_zero` is the initial velocity (denoted by $u_0$);
- `x_bump` is the position of the bump (denoted by $x_b$);
- `width_bump` is the width of the bump (denoted by $\ell$).

The bump function with $n$ continous derivatives is then defined by

$$
\phi_n(x) = \rho_g + \left\lbrace
\begin{aligned}
    &0&& \text{if } &&x \leq x_b-\ell,\\
    & \frac{\rho_b-\rho_g}{l^{2n}}
        (x_b+\ell-x)^n(x-x_b+\ell)^n && \text{if } &x_b-\ell \leq &\;x \leq x_b+\ell,\\
    &\rho_g&& \text{if } &x_b+\ell\leq &\;x.
\end{aligned}
\right.
$$

**Discontinous bump function**

The parameter `reg` can also take the value $-1$. In that case, the initial function is a discontinuous function with two values: the ground value `rho_ground` and the bump value `rho_bump`.

$$
\phi_{-1}(x) = \left\lbrace
\begin{aligned}
    &\rho_g&& \text{if } &&x \leq x_b-\ell,\\
    &\rho_b&& \text{if } &x_b-\ell \leq &\;x \leq x_b+\ell,\\
    &\rho_g&& \text{if } &x_b+\ell\leq &\;x.
\end{aligned}
\right.
$$

**Figure**

![](./hyperbolic_1D/1_acoustics/image_bump.png "The bump functions")