An **indicator** function or **characteristic** function is a discontinuous function that indicates if an element is inside or outside a given set. 

In order to investigate the behavior of the schemes, we consider both **indicator** function of an interval or intermediate regularization of it.
These functions are all compactly supported and the regularity can be chosen with the parameter `reg`.

**Construction** of the functions

We explain how we construct a function with $n$ continuous derivatives in dimension $1$. This function is obtained by combining the polynomial functions $P_n$ (described bellow) to link the two constant states (`u_bottom` and `u_top`).

The notations are the following:

- `reg` is the number of continuous derivatives of the fields $u$ (denoted by $n$);
- `pos_left` is the position of the left bound (denoted by $x_l$);
- `pos_right` is the position of the right bound (denoted by $x_r$);
- `width_left` is the width of the regularization at the left (denoted by $d_l$;
- `width_right` is the width of the regularization at the right (denoted by $d_r$;
- `u_out` is the value of the fields $u$ outside the interval (denoted by $u_{\text{out}}$);
- `u_in` is the value inside the interval (denoted by $u_{\text{in}}$);
 
 A picture is worth a thousand words:

![indicator](./Dimension1/Advection/image_indicator.png "The indicator functions")

**Construction of the polynomials $P_n$**

We construct an odd polynomial function denoted by $P_n$ defined on $[-1, 1]$ which satisfies
$$
P_n(\pm 1) = \pm 1, \quad
P_n^{(k)}(\pm 1) = 0, \quad 1\leq k\leq n,
$$
where we have denoted $P_n^{(k)}$ the $k$-th derivative of $P_n$.
As we have to satisfy $2n+2$ relations, its degree can be $2n+1$.

Observing that the first derivative $P_n'$ is even, with a degree $2n$, we choose
$$
P_n'(X) = C_n(1-X^2)^n,
$$
where $C_n$ is a real value fixed by the relation $P_n(1)=1$. The polynomial function $P_n$ is then defined by
$$
P_n(X) = C_n \int_0^X (1-x^2)^n \; dx.
$$
We then have a recursive relation
$$
P_n(X) 
= \frac{C_n}{C_{n-1}} P_{n-1} - C_n \int_0^X x^2(1-x^2)^{n-1} \; dx
$$
that can be resolved by integrating by parts:
$$
(1+2n)P_n(X) = C_n \left(
    \frac{2n}{C_{n-1}} P_{n-1}(X) + X(1-X^2)^n.
\right)
$$
Writting $P_n(1)=1$ yields
$$
C_n = \bigl(1+\frac{1}{2n}\bigr)C_{n-1}.
$$
The initialization is given for $n=0$ by $P_0(X)=X$ and $C_0=1$.

![P_n](./Dimension1/Advection/image_indicator_Pn.png "The polynomial functions")

