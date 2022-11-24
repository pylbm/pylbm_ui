This two-dimensional test problem was introduced by Emery in the publication [1] in which several different schemes are compared. Woodward and Colella[2] presented the solutions obtained with MUSCL approach and still prove that this test be a benchmark case. The problem begins with uniform Mach 3 flow in a wind tunnel containing a step. The wind tunnel is 1 length unit wide and 3 length units long. The step is 0.2 length units high and is located 0.6 length units from the left-hand end of the tunnel. The tunnel is assumed to have an infinite width in the direction orthogonal to the plane of the computation (i.e., symmetric boundaries in the third dimension are assumed). At the left is an inflow boundary condition, and at the right, all gradients are assumed to vanish. The exit boundary condition has no effect on the flow, because the exit velocity is always supersonic. Initially, the wind tunnel is filled with a gamma-law gas, with $\gamma = 1.4$, which everywhere has density 1.4, pressure 1.0, and velocity 3. Gas with this density, pressure, and velocity is continually fed in from the left-hand boundary.

![](./Dimension2/Euler/ffs.png "Forward facing step"){ width=50% }

Very simple problem to setup, and visualize but complex flow which allows qualitative check of the solution. The purpose is to test the solution at the corner, rectilinear lattice but non-aligned complex shock patterns, shock interactions, reflections, perpendicularity to the walls. Inviscid flow symmetry boundary condition is the same as the inviscid wall condition. So in all solid and symmetric surfaces, derivatives perpendicular to the wall vanish.

Visual comparison of the density isolines of the solution at time t=4s is to be performed with the results of [2].

![](./Dimension2/Euler/ffs_mach3.png "Solution given in [2]"){ width=50% }

> [[1] Emery, A., *An evaluation of several differencing methods for inviscid fluid flow problems* (JCP, **2**, 1968)](https://www.sciencedirect.com/science/article/pii/0021999168900600)
>
> [[2] Woodward, P. \& Colella, P. *The numerical simulation of two-dimensional fluid flow with strong shocks* (JCP, **54**, 1984)](https://www.sciencedirect.com/science/article/pii/0021999184901426)
