# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#
# License: BSD 3 clause
"""
Advection
"""

from .riemann_solvers import GenericSolver


class AdvectionSolver(GenericSolver):
    """
        d_t(u) + c d_x(u) = 0
    """
    def _read_particular_parameters(self, parameters):
        self.velocity = parameters.get('velocity', 1)
        self.fields = parameters.get('fields name', [r'$u$'])

    def _compute_waves(self):
        self.values.append(self.u_left)
        self.velocities.append([
            self.velocity, self.velocity
        ])
        self.values.append(None)
        self.waves.append('shock')
        self.values.append(self.u_right)
