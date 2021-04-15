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

class tc_2D_FFS(HashBaseModel):
    xmin: float
    xmax: float
    ymin: float
    ymax: float

    step_xmin: float
    step_ymax: float

    rho_in: float
    ux_in: float
    uy_in: float
    p_in: float

    gamma: float
    duration: float

    dim=2
    equation = Euler2D()
    name = 'FFS'
    BCType  = 'none'
    description = 'none'
    responses = {}

    def get_dictionary(self):

        def init_rho(x, y):
            #stepMask = (x >= self.xmin+self.step_xmin) * (y <= self.ymin+self.step_ymax)
            #return stepMask * 0. + np.logical_not(stepMask) * self.rho_in
            return self.rho_in
        def init_ux(x, y):
            #stepMask = (x >= self.xmin+self.step_xmin) * (y <= self.ymin+self.step_ymax)
            #return stepMask * 0. + np.logical_not(stepMask) * self.ux_in
            return self.ux_in
        def init_uy(x, y):
            #stepMask = (x >= self.xmin+self.step_xmin) * (y <= self.ymin+self.step_ymax)
            #return stepMask * 0. + np.logical_not(stepMask) * self.uy_in
            return self.uy_in
        def init_p(x, y):
            #stepMask = (x >= self.xmin+self.step_xmin) * (y <= self.ymin+self.step_ymax)
            #return stepMask * 0. + np.logical_not(stepMask) * self.p_in
            return self.p_in
        def init_qx(x, y):
            return init_rho(x, y) * init_ux(x, y)
        def init_qy(x, y):
            return init_rho(x, y) * init_uy(x, y)
        def init_E(x, y):
            return .5*init_rho(x, y)*(init_ux(x, y)**2 + init_uy(x, y)**2) + init_p(x, y)/(self.gamma-1)

        BC_labels = [1,1,4,4]
        step_BC_labels = [3, 3, 4, 4]

        return {
            'box': {
                'x': [self.xmin, self.xmax],
                'y': [self.ymin, self.ymax],
                'label': BC_labels
            },
            'elements': [pylbm.Parallelogram((self.xmin+self.step_xmin,self.ymin) , (self.xmax, self.ymin), (self.xmin, self.ymin+self.step_ymax),
                                             label=step_BC_labels)],

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
        return self.xmax - self.xmin

    def get_boundary(self):
        return {
            0: self.equation.NonReflexiveOutlet,
            1: self.equation.Neumann,
            2: self.equation.Dirichlet_u,
            3: self.equation.Symmetry_Y,
            4: self.equation.Symmetry_X
        }

    def state(self):
        return [{self.equation.rho: self.rho_in,
                 self.equation.qx: self.rho_in*self.ux_in,
                 self.equation.qy: self.rho_in*self.uy_in,
                 self.equation.E: 0.5*self.rho_in*(self.ux_in**2.*self.uy_in**2.) + self.p_in/(self.gamma-1.),
                },
        ]

##################################
### predefined cases
##################################

FFS_Ma3 = tc_2D_FFS(
    name = 'FFS_Ma3',
    xmin = 0., xmax = 3.,
    ymin = 0., ymax = 1.,
    step_xmin = 0.6, step_ymax = 0.2,

    rho_in=1.4,
    ux_in=3.,
    uy_in=0.,
    p_in=1.,

    gamma = 1.4,
    duration = 5.,

    description =
"""FFS 2D is a 2D test case proposed in....

"""
    )





