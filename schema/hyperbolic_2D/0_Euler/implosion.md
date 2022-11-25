The purpose is to test the accuracy of the scheme.
The case, used in the Liska&Wendroff test suite[1] and previously introduced in [2], is very sensitive to the ability of the algorithm to maintain symmetry across the diagonal $x = y$, (rotational invariance 2D Sod shock tube problem).
Moreover, it can be used to measure the rate of numerical diffusion of contact discontinuities.

The solution is initialized with the conditions lower density and pressure inside the inner green square, whose sides are diaphragms. Flow is stagnant, and at t=0 the diaphragms break symmetric jets form. A quarter of the domain with all symmetric boundary conditions is solved.

![](./Dimension2/Euler/implosion.png "implosion test case"){ width=25% }

<table style="border:1px solid black">
    <thead align="center">
        <tr style="border:1px solid black">
            <th style="border:1px solid black; text-align: center; background-color: rgba(50, 150, 50, 0.6)">$\rho_{\text{in}}$</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(50, 150, 50, 0.6)">$v_{\text{in}}$</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(50, 150, 50, 0.6)">$p_{\text{in}}$</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$\rho_{\text{out}}$</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$v_{\text{out}}$</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$p_{\text{out}}$</th>
            <th style="border:1px solid black; text-align: center">$\gamma$</th>
        </tr>
    </thead>
    <tbody align="center">
        <tr style="border:1px solid black">
            <td style="border:1px solid black; text-align: center; background-color: rgba(50, 150, 50, 0.6)">$0.125$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(50, 150, 50, 0.6)">$0$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(50, 150, 50, 0.6)">$0.14$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$1$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$0$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$1$</td>
            <td style="border:1px solid black; text-align: center">$1.4$</td>
        </tr>
    </tbody>
</table>

Comparison data is the visual check of the 2D density field of 0.35 to 1.1 with a step of 0.025 at time t=2.5s, with Princeton Athena code implosion test page, and the Liska&Wendroff test suite contributions,[1].

![](./Dimension2/Euler/implode_dens_cont.png "solution"){ width=50% }


> [[1] Liska, R., \& Wendroff *Comparison of several difference schemes on 1D and 2D test problems for the Euler equations* (SIAM Journal on scientific Computing, **25**, p.995, 2003)](https://rsaa.anu.edu.au/files/liska_wendroff_2003.pdf)
>
> [[2] Hui, W.H., \& Li, P.Y., \& Li, Z.W *A unified coordinate system for solving the two dimensional euler equations* (JCP, **153**, p.596, 1999)](https://www.sciencedirect.com/science/article/pii/S0021999199962952)

