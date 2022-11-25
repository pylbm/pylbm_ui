For this test case, the density $\rho$ and the momentum $q$ read

$$
\rho(t, x) = \sin(\xi x - \omega t),
\quad
q(t, x) = (\bar u+c) \sin(\xi x - \omega t),
$$

where $\omega = \xi (\bar u+c)$.

In order to avoid the problem of the boundary conditions, the wave number $\xi$ is adapted to the domain length:

$$
\xi = \frac{2\pi k}{x_{\text{max}}-x_{\text{min}}},
$$

where $k$ is a positive integer, $x_{\text{min}}$ and $x_{\text{max}}$ the left and right bounds of the domain.

**The parameters** of this test case are

- `c` the acoustics velocity;
- `u_bar` the advective velocity;
- `k` the scaled wave number;
- `xmin` and `xmax` the bounds of the domain.