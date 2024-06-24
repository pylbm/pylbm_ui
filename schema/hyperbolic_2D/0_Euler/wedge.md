Supersonic wedge is an example study demonstrating the computational process using a simple supersonic flow past a wedge with a comparison of the results with analytical results. The problem is to compute the exit Mach number and the shock angle, given fix parallel, uniform inlet Mach number at 2.5 or 8 and the wedge angle 15 deg. The analytical 1-D oblique shock relations define the shock angle and the state after the wedge.

![](./Dimension2/Euler/wedge.png "wedge test case")

The computation of the shock angle, being given the wedge angle and the inlet Mach number is done by solving a non-linear equation. Follow this link:
[https://www.engineering.com/calculators/oblique_flow_relations.htm](https://www.engineering.com/calculators/oblique_flow_relations.htm)

<table style="border:1px solid black">
    <thead align="center">
        <tr style="border:1px solid black">
            <th style="border:1px solid black; text-align: center; background-color: rgba(26, 188, 156, 0.5)">Mach inlet</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(26, 188, 156, 0.5)">Wedge angle $\theta$</th>
            <th style="border:1px solid black; text-align: center">AoA</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">Mach outlet</th>
            <th style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">Shock angle $\beta$</th>
        </tr>
    </thead>
    <tbody align="center">
        <tr style="border:1px solid black">
            <td style="border:1px solid black; text-align: center; background-color: rgba(26, 188, 156, 0.5)">$2.5$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(26, 188, 156, 0.5)">$15^{\circ}$</td>
            <td style="border:1px solid black; text-align: center">$0^{\circ}$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$1.8735$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$36.945^{\circ}$</td>
        </tr>
        <tr style="border:1px solid black">
            <td style="border:1px solid black; text-align: center; background-color: rgba(26, 188, 156, 0.5)">$8$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(26, 188, 156, 0.5)">$15^{\circ}$</td>
            <td style="border:1px solid black; text-align: center">$0^{\circ}$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$4.7478$</td>
            <td style="border:1px solid black; text-align: center; background-color: rgba(253, 211, 0, 0.5)">$20.806^{\circ}$</td>
        </tr>
    </tbody>
</table>

For a wedge angle equal to 15 degrees, the outlet Mach number and the shock angle are plotted according to the inlet Mach number:

![](./Dimension2/Euler/wedge_theta_15.png)

**Method to compute the shock angle and the Mach outlet**

Denoting $\theta$ the wedge angle, $\rho_{\text{in}}$, $v_{\text{in}}$, and $p_{\text{in}}$ the inlet values of the mass, the norm of the velocity, and the pressure, the Rankine-Hugoniot relations yields
$$
\left\lbrace
\begin{aligned}
\rho_{\text{out}} &= \rho_{\text{in}} \frac{\tan(\beta)}{\tan(\beta-\theta)},\\
v_{\text{out}} &= v_{\text{in}} \frac{\cos(\beta)}{\cos(\beta-\theta)},\\
p_{\text{out}} &= p_{\text{in}} + \rho_{\text{in}}v_{\text{in}}^2 
\frac{\sin(\beta)\sin(\theta)}{\cos(\beta-\theta)},
\end{aligned}
\right.
$$
where $\beta$ is the shock angle given as the smallest zero (if there is one) of the function $\varphi$ with
\begin{align*}
\varphi(\alpha) & = 
(\gamma-1) M_{\text{in}}^2 \tan(\alpha) 
\left[
\frac{1}{2} \Big(\cos^2(\alpha-\theta)-\cos^2(\alpha)\Big)
- \frac{\gamma}{\gamma-1} \cos(\alpha)\sin(\theta)\sin(\alpha-\theta)
\right] \\
& \phantom{=}\; - \cos^2(\alpha-\theta)\Big(\tan(\alpha-\theta)-\tan(\alpha)\Big),
\end{align*}
where the inlet Mach number $M_{\text{in}} = \sqrt{\rho_{\text{in}}v_{\text{in}}^2/(\gamma p_{\text{in}})}$.