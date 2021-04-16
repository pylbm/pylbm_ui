# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
from pydantic import BaseModel
import numpy as np
import pylbm
import matplotlib.pyplot as plt

from .equation_type import EquationType, Euler2D
from .utils import HashBaseModel

class tc_2D_wedge(HashBaseModel):
    xmin: float
    xmax: float
    ymin: float
    ymax: float

    rho_in: float
    ux_in: float
    uy_in: float
    p_in: float

    gamma: float
    duration: float

    dim=2
    equation = Euler2D()
    name = 'Wedge2D'
    BCType  = 'none'
    description = 'none'
    responses = {}

    def get_dictionary(self):

        def init_rho(x, y):
            return self.rho_in
        def init_ux(x, y):
            return self.ux_in
        def init_uy(x, y):
            return self.uy_in
        def init_p(x, y):
            return self.p_in
        def init_qx(x, y):
            return init_rho(x, y) * init_ux(x, y)
        def init_qy(x, y):
            return init_rho(x, y) * init_uy(x, y)
        def init_E(x, y):
            return .5*init_rho(x, y)*(init_ux(x, y)**2 + init_uy(x, y)) + init_p(x, y)/(self.gamma-1)

        BC_labels = [1, 1, 4, 1]

        angle = 15. * np.pi/180.;
        tri_p1 = [self.xmin + (self.xmax-self.xmin)*0.2, self.ymin]
        tri_p2 = [self.xmax, ( self.xmax - tri_p1[0] )*np.tan(angle) ]
        tri_p3 = [self.xmax, self.ymin]

        return {
            'box': {
                'x': [self.xmin, self.xmax],
                'y': [self.ymin, self.ymax],
                'label': BC_labels
            },
            'elements': [pylbm.Triangle( (tri_p1[0],tri_p1[1]) , (tri_p2[0],tri_p2[1]), (tri_p3[0],tri_p3[1]), label=2 )],
            'init': {
                self.equation.rho: init_rho,
                self.equation.qx: init_qx,
                self.equation.qy: init_qy,
                self.equation.E: init_E,
            },
            'parameters': {
                self.equation.gamma: self.gamma
            }
        }

    def size(self):
        return [self.xmax - self.xmin, self.ymax - self.ymin]

    def get_boundary(self):
        return {
            0: self.equation.NonReflexiveOutlet,
            1: self.equation.Neumann,
            2: self.equation.Dirichlet_u,
            3: self.equation.Symmetry_Y,
            4: self.equation.Symmetry_X
        }

    def state(self):
        return  [{self.equation.rho: self.rho_in,
                  self.equation.qx: self.rho_in*self.ux_in,
                  self.equation.qy: self.rho_in*self.uy_in,
                  self.equation.E: 0.5*self.rho_in*(self.ux_in**2.*self.uy_in**2.) + self.p_in/(self.gamma-1.),
                 },
        ]

##################################
### predefined cases
##################################

Wedge_Ma2p5 = tc_2D_wedge(
    name = 'Wedge_Ma2p5',
    xmin = 0., xmax = 3.,
    ymin = 0., ymax = 2.,
    rho_in=1.4,
    ux_in=2.5,
    uy_in=0.,
    p_in=1.,

    gamma = 1.4,
    duration = 5.,



    description =
"""Wedge 2D is a 2D test case proposed in....

"""
    )
Wedge_Ma8 = tc_2D_wedge(
    name = 'Wedge_Ma8',
    xmin = 0., xmax = 3.,
    ymin = 0., ymax = 2.,
    rho_in=1.4,
    ux_in=8,
    uy_in=0.,
    p_in=1.,

    gamma = 1.4,
    duration = 5.,



    description =
"""Wedge 2D is a 2D test case proposed in....

"""
    )




