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

from .equation_type import Euler2D
from ...utils import HashBaseModel

class tc_2D_implosion2D(HashBaseModel):
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    trisize: float

    rho_left: float
    rho_right: float
    ux_left: float
    ux_right: float
    uy_left: float
    uy_right: float
    p_left: float
    p_right: float

    gamma: float
    duration: float

    dim=2
    equation = Euler2D()
    name = 'Implosion2D'
    BCType  = 'none'
    description = 'none'
    responses = {}

    def get_dictionary(self):

        def init_rho_Impl(x, y):
            mask = (np.abs(x) + np.abs(y) <= self.trisize)
            return self.rho_left*mask + self.rho_right*np.logical_not(mask)

        def init_ux_Impl(x, y):
            mask = (np.abs(x) + np.abs(y) <= self.trisize)
            return self.ux_left*mask + self.ux_right*np.logical_not(mask)

        def init_uy_Impl(x, y):
            mask = (np.abs(x) + np.abs(y) <= self.trisize)
            return self.uy_left*mask + self.uy_right*np.logical_not(mask)

        def init_p_Impl(x, y):
            mask = (np.abs(x) + np.abs(y) <= self.trisize)
            return self.p_left*mask + self.p_right*np.logical_not(mask)

        def init_qx_Impl(x, y):
            return init_rho_Impl(x, y) * init_ux_Impl(x, y)

        def init_qy_Impl(x, y):
            return init_rho_Impl(x, y) * init_uy_Impl(x, y)

        def init_E_Impl(x, y):
            return .5*init_rho_Impl(x, y)*(init_ux_Impl(x, y)**2 + init_uy_Impl(x, y)**2) + \
                init_p_Impl(x, y)/(self.gamma-1)

        BC_labels = [-1,-1,-1,-1]
        if (self.BCType == "symmetric"):
            BC_labels = [3, 3, 4, 4]

        return {
            'box': {
                'x': [self.xmin, self.xmax],
                'y': [self.ymin, self.ymax],
                'label': BC_labels
            },
            'init': {
                self.equation.rho: init_rho_Impl,
                self.equation.qx: init_qx_Impl,
                self.equation.qy: init_qy_Impl,
                self.equation.E: init_E_Impl,
            },
            'parameters': {
                self.equation.gamma: self.gamma
            }
        }

    def size(self):
        return [self.xmax - self.xmin, self.ymax - self.ymin]

    def set_size(self, size):
        self.xmax = self.xmin + size[0]
        self.ymax = self.ymin + size[1]

    def get_boundary(self):
        return {
            0: self.equation.NonReflexiveOutlet,
            1: self.equation.Neumann,
            2: self.equation.Dirichlet_u,
            3: self.equation.Symmetry_Y,
            4: self.equation.Symmetry_X
        }

    def state(self):
        return [{self.equation.rho: self.rho_left,
                 self.equation.qx: self.rho_left*self.ux_left,
                 self.equation.qy: self.rho_left*self.uy_left,
                 self.equation.E: 0.5*self.rho_left*(self.ux_left**2.*self.uy_left**2.) + self.p_left/(self.gamma-1.),
                },
                {self.equation.rho: self.rho_right,
                 self.equation.qx: self.rho_right*self.ux_right,
                 self.equation.qy: self.rho_right*self.uy_right,
                 self.equation.E: 0.5*self.rho_right*(self.ux_right**2.*self.uy_right**2.) + self.p_right/(self.gamma-1.)
                },
        ]

##################################
### predefined cases
##################################

Implosion2D_Symmetric = tc_2D_implosion2D(
    xmin = 0., xmax = 0.3,
    ymin = 0., ymax = 0.3,
    trisize = 0.150001,

    rho_left=0.125, rho_right=1.,
    ux_left=0., ux_right=0.,
    uy_left=0., uy_right=0.,
    p_left=0.14, p_right=1.,

    gamma=1.4,
    duration=2.5, # ~0.4 pour que le choc atteigne le coin oppose

    name = 'Implosion2D_Symmetric',
    BCType = "symmetric",

    description =
"""Implosion 2D is a 2D test case proposed in....

"""
)
