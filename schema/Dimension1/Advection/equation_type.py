# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
# from pydantic import BaseModel
import sympy as sp

from ...symbol import Symbol
from ...equation_type import EquationType


class Transport1D(EquationType):
    name = 'Advection with constant velocity'
    u = Symbol('u')
    c = Symbol('c')
    NonReflexiveOutlet = 'NonReflexiveOutlet'
    Neumann = 'Neumann'
    Dirichlet_u = 'Dirichlet_u'

    def get_fields(self):
        fields = {
            'mass': self.u,
        }
        return fields

    @property
    def description(self):
        return """
> [*From Wikipedia, the free encyclopedia* ](https://en.wikipedia.org/wiki/Advection)
>
> In the field of physics, engineering, and earth sciences, advection is the transport of a substance or quantity by bulk motion of a fluid. The properties of that substance are carried with it. Generally the majority of the advected substance is a fluid. The properties that are carried with the advected substance are conserved properties such as energy. An example of advection is the transport of pollutants or silt in a river by bulk water flow downstream. Another commonly advected quantity is energy or enthalpy. Here the fluid may be any material that contains thermal energy, such as water or air. In general, any substance or conserved, extensive quantity can be advected by a fluid that can hold or contain the quantity or substance.
>
> During advection, a fluid transports some conserved quantity or material via bulk motion. The fluid's motion is described mathematically as a vector field, and the transported material is described by a scalar field showing its distribution over space. Advection requires currents in the fluid, and so cannot happen in rigid solids. It does not include transport of substances by molecular diffusion.
>
> Advection is sometimes confused with the more encompassing process of convection which is the combination of advective transport and diffusive transport.
>
> In meteorology and physical oceanography, advection often refers to the transport of some property of the atmosphere or ocean, such as heat, humidity (see moisture) or salinity. Advection is important for the formation of orographic clouds and the precipitation of water from clouds, as part of the hydrological cycle.

The advection equation in dimension 1 is
the simplest model of hyperbolic equation.
Denoting $c$ a real constant, the scalar quantity $u(t, x)$,
where $t$ is the time and $x$ the one-dimensional space variable,
satisfies the advection equation

$$
    \\left\\lbrace\\begin{aligned}
    &\partial_t u(t,x) + c \partial_x u(t,x) = 0,&& t>0, \ x\in\mathbb{R},\\\\
    &u(0,x) = u_0(x), && x\in\mathbb{R},
    \\end{aligned}\\right.
$$

where $u_0$ is a given function (the initial configuration).

The solution of the advection equation is given by

$$
    u(t, x) = u_0(x-ct), \qquad t>0, \ x\in\mathbb{R}.
$$
        """
