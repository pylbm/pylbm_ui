Toro [1] gives five different versions of the Sod's shock tube test,
which differ only in the initial data but each one is designed
with a specific target.
The initial data is defined by the left and the right states
given in the Table at t=0 at which the diaphragm is broken.
At t$>$0, depending on the initial data, there are
**contact discontinuities**, **shocks** and, **expansion** waves.

<table style="border:1px solid black">
    <thead align="center">
        <tr style="border:1px solid black">
            <th style="border:1px solid black; text-align: center"></th>
            <th style="border:1px solid black; text-align: center">Toro 1</th>
            <th style="border:1px solid black; text-align: center">Toro 2</th>
            <th style="border:1px solid black; text-align: center">Toro 3</th>
            <th style="border:1px solid black; text-align: center">Toro 4</th>
            <th style="border:1px solid black; text-align: center">Toro 5</th>
        </tr>
    </thead>
    <tbody align="center">
        <tr style="border:1px solid black">
            <th>mass left</th>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">5.99924</td>
        </tr>
        <tr style="border:1px solid black">
            <th>velocity left</th>
            <td style="border:1px solid black; text-align: center">0</td>
            <td style="border:1px solid black; text-align: center">-2</td>
            <td style="border:1px solid black; text-align: center">0</td>
            <td style="border:1px solid black; text-align: center">0</td>
            <td style="border:1px solid black; text-align: center">19.5975</td>
        </tr>
        <tr style="border:1px solid black">
            <th>pressure left</th>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">0.4</td>
            <td style="border:1px solid black; text-align: center">1000</td>
            <td style="border:1px solid black; text-align: center">0.01</td>
            <td style="border:1px solid black; text-align: center">460.894</td>
        </tr>
        <tr style="border:1px solid black">
            <th>mass right</th>
            <td style="border:1px solid black; text-align: center">0.125</td>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">5.99242</td>
        </tr>
        <tr style="border:1px solid black">
            <th>velocity right</th>
            <td style="border:1px solid black; text-align: center">0</td>
            <td style="border:1px solid black; text-align: center">1</td>
            <td style="border:1px solid black; text-align: center">0</td>
            <td style="border:1px solid black; text-align: center">0</td>
            <td style="border:1px solid black; text-align: center">-6.19633</td>
        </tr>
        <tr style="border:1px solid black">
            <th>pressure right</th>
            <td style="border:1px solid black; text-align: center">0.1</td>
            <td style="border:1px solid black; text-align: center">0.4</td>
            <td style="border:1px solid black; text-align: center">0.01</td>
            <td style="border:1px solid black; text-align: center">100</td>
            <td style="border:1px solid black; text-align: center">46.095</td>
        </tr>
    </tbody>
</table>

Toro test case 3 tests the accuracy and robustness.
The solution consists of a strong shock
wave, a contact surface and a left rarefaction wave.
The strong shock wave is of Mach number 1.98.
The analytical solution computed with the computer program from Toro
is plotted in the next Figure.

![](./hyperbolic_1D/5_Euler/Toro_Test3.png "Toro test case 3")

The test case parameters can be modified using
the "Test case parameters" panel below

The reference final results are computed using an exact Riemann solver
that compute the two intermediate states.
The `fsolve` function of the module `scipy.optimize` is used.

> [[1] Eleuterio F. Toro, Riemann Solvers and Numerical Methods for Fluid Dynamics, March 2009, DOI:10.1007/b79761*3
> In book: \_Riemann Solvers and Numerical Methods for Fluid Dynamics* (pp.87-114)](https://www.researchgate.net/publication/278720679_Riemann_Solvers_and_Numerical_Methods_for_Fluid_Dynamics)
>
> [[2] Gary A. Sod, _A Survey of Several Finite Difference Methods for Systems of Nonlinear Hyperbolic Conservation Laws_, J. Comput. Phys. **27** (pp. 1–31) 1978](https://hal.archives-ouvertes.fr/hal-01635155/file/GAS.pdf)
