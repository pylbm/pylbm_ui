> [_From Wikipedia, the free encyclopedia_](https://en.wikipedia.org/wiki/Euler_equations_(fluid_dynamics))
>
> The Euler equations first appeared in published form in Euler's article "Principes généraux du mouvement des fluides", published in Mémoires de l'Académie des Sciences de Berlin in 1757 (in this article Euler actually published only the general form of the continuity equation and the momentum equation; the energy balance equation would be obtained a century later). They were among the first partial differential equations to be written down. At the time Euler published his work, the system of equations consisted of the momentum and continuity equations, and thus was underdetermined except in the case of an incompressible fluid. An additional equation, which was later to be called the adiabatic condition, was supplied by Pierre-Simon Laplace in 1816.
>
> During the second half of the 19th century, it was found that the equation related to the balance of energy must at all times be kept, while the adiabatic condition is a consequence of the fundamental laws in the case of smooth solutions. With the discovery of the special theory of relativity, the concepts of energy density, momentum density, and stress were unified into the concept of the stress–energy tensor, and energy and momentum were likewise unified into a single concept, the energy–momentum vector.

The Euler equations consist of a system of conservation laws on the fluid mass density $\rho$, the momentum density $q=(q_x, q_y)$, and the total energy density $E$.
These quantities are linked with the velocity $u$ and the pressure $p$ by the relations
$$
q_x = \rho u_x, \qquad q_y = \rho u_y, \qquad E = \frac{1}{2}\rho (u_x^2+u_y^2) + \frac{p}{\gamma-1},
$$
with $\gamma$ the heat capacity ratio.
In dimension $1$, the system reads
$$
    \left\lbrace\begin{aligned}
    &\partial_t \rho + \partial_x (\rho u_x) + \partial_y (\rho u_y)= 0,\\
    &\partial_t (\rho u_x) + \partial_x (\rho u_x^2+p) + \partial_y (\rho u_x u_y) = 0,\\
    &\partial_t (\rho u_y) + \partial_x (\rho u_x u_y) + \partial_y (\rho u_y^2+p) = 0,\\
    &\partial_t E + \partial_x ((E+p)u_x) + \partial_y ((E+p)u_y) = 0,
    \end{aligned}\right.
$$
where we have omitted the dependency in the time variable $t$ and in the space variable $x$ for clarity.

The system is hyperbolic and the three eigenvalues of the jacobian matrix are $u-c$, $u$, and $u+c$ where $c = \sqrt{\gamma p/\rho}$ is the speed of sound.