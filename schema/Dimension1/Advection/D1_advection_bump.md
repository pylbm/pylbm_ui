A **bump** function is both smooth (in the sense of having continuous derivatives of all orders) and compactly supported.
In order to investigate the behaviour of the schemes, we also consider **indicator** function of an intervalle or intermadiate regularization of it.
These functions are all compactly supported and their regularity can be chosen with the parameter `reg`.

**Regular bump functions**

The bump functions we consider are piecewise polynomial functions.
The notations are the following:

- `reg` is the number of continuous derivatives of the fields $u$ (denoted by $n$);
- `u_ground` is the ground value of the fields $u$ (denoted by $u_g$);
- `u_bump` is the top value on the bump (denoted by $u_b$);
- `x_bump` is the position of the bump (denoted by $x_b$);
- `width_bump` is the width of the bump (denoted by $\ell$).

The bump function with $n$ continous derivatives is then defined by
$$
\phi_n(x) = u_g + \left\lbrace
\begin{aligned}
    &0&& \text{if } &&x \leq x_b-\ell,\\
    & \frac{u_b-u_g}{l^{2n}}
        (x_b+\ell-x)^n(x-x_b+\ell)^n && \text{if } &x_b-\ell \leq &\;x \leq x_b+\ell,\\
    &u_g&& \text{if } &x_b+\ell\leq &\;x.
\end{aligned}
\right.
$$

**Discontinous bump function**

The parameter `reg` can also take the value $-1$. In that case, the initial function is a discontinuous function with two values: the ground value `u_ground` and the bump value `u_bump`.

$$
\phi_{-1}(x) = \left\lbrace
\begin{aligned}
    &u_g&& \text{if } &&x \leq x_b-\ell,\\
    &u_b&& \text{if } &x_b-\ell \leq &\;x \leq x_b+\ell,\\
    &u_g&& \text{if } &x_b+\ell\leq &\;x.
\end{aligned}
\right.
$$

**Figure**

![](./Dimension1/Advection/image_bump.png "The bump functions")