# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#
# License: BSD 3 clause
"""
compressible Euler (with temperature)
"""

import numpy as np
import matplotlib.pyplot as plt
from .riemann_solvers import GenericSolver, solve


class EulerSolver(GenericSolver):
    """
    d_t(rho)   + d_x(rho u)     = 0,
    d_t(rho u) + d_x(rho u^2+p) = 0,
    d_t(E)   + d_x((E+p) u)     = 0,

    where E and p are linked by E = 1/2 rho u^2 + p/(gamma-1)

    then p = (gamma-1)(E - rho u^2/2)
    rho u^2 + p = (gamma-1)E + rho u^2 (3-gamma)/2
    E + p = 1/2 rho u^2 + p

    The 3 variables used to parametrize the solution are
    rho, u, and p.
    """
    def __init__(self, parameters):
        self.rho_k1 = self.u_k1 = self.p_k1 = self.lambda_l = None
        self.rho_k3 = self.u_k3 = self.p_k3 = self.lambda_r = None
        super().__init__(parameters)

    def _read_particular_parameters(self, parameters):
        self.gamma = parameters.get('gamma', 1.4)
        self.mu2 = (self.gamma-1) / (self.gamma+1)
        self.fields = parameters.get(
            'fields name',
            [r'$\rho$', r'$u$', r'$p$']
        )

    def _compute_interstate(self):
        """
        Compute the intermediate state
        """
        p_star = solve(
            self._f1, self._f2,
            self.u_left[2], self.u_right[2],
            self.epsilon
        )
        u_star = .5*(self._f1(p_star)[0]+self._f2(p_star)[0])
        # compute rho_star
        if p_star < self.u_left[2]:  # 1-rarefaction
            rho_star1 = self.u_left[0] * (
                p_star / self.u_left[2]
            )**(1/self.gamma)
        else:  # 1-shock
            rho_star1 = self.u_left[0] * (
                (p_star+self.mu2*self.u_left[2]) /
                (self.mu2*p_star+self.u_left[2])
            )
        if p_star < self.u_right[2]:  # 3-rarefaction
            rho_star2 = self.u_right[0] * (
                p_star / self.u_right[2]
            )**(1/self.gamma)
        else:  # 3-shock
            rho_star2 = self.u_right[0] * (
                (p_star+self.mu2*self.u_right[2]) /
                (self.mu2*p_star+self.u_right[2])
            )
        self.u_star = [
            np.array([rho_star1, u_star, p_star]),
            np.array([rho_star2, u_star, p_star])
        ]

    def _rarefaction_1(self, xik):
        if self.rho_k1 is None:
            rho_l, u_l, p_l = self.u_left
            c_l = np.sqrt(self.gamma*p_l/rho_l)
            self.lambda_l = u_l - c_l

            self.rho_k1 = [
                np.sqrt(rho_l**(self.gamma-1)),
                - np.sqrt(rho_l**self.gamma / (self.gamma*p_l)) * (self.gamma-1)
            ]
            self.u_k1 = u_l
            self.p_k1 = p_l*rho_l**-self.gamma

        dummy = (xik - self.lambda_l) / (self.gamma+1)
        rho_k = (self.rho_k1[0] + self.rho_k1[1]*dummy)**(2/(self.gamma-1))
        return [
            rho_k,
            self.u_k1 + 2 * dummy,
            self.p_k1 * rho_k**self.gamma]

    def _rarefaction_3(self, xik):
        if self.rho_k3 is None:
            rho_r, u_r, p_r = self.u_right
            c_r = np.sqrt(self.gamma*p_r/rho_r)
            self.lambda_r = u_r + c_r
            self.rho_k3 = [
                np.sqrt(rho_r**(self.gamma-1)),
                np.sqrt(rho_r**self.gamma / (self.gamma*p_r)) * (self.gamma-1)
            ]
            self.u_k3 = u_r
            self.p_k3 = p_r*(rho_r)**-self.gamma

        dummy = (xik - self.lambda_r) / (self.gamma+1)
        rho_k = (self.rho_k3[0] + self.rho_k3[1]*dummy)**(2/(self.gamma-1))
        return [
            rho_k,
            self.u_k3 + 2 * dummy,
            self.p_k3 * rho_k**self.gamma]

    def _compute_waves(self):
        """
        Compute the 3 waves, the intermediate state being computed
        """
        self.values.append(self.u_left)
        rho_l, u_l, p_l = self.u_left
        rho_s1, u_s1, p_s1 = self.u_star[0]
        rho_s2, u_s2, p_s2 = self.u_star[1]
        rho_r, u_r, p_r = self.u_right
        c_l = np.sqrt(self.gamma*p_l/rho_l)
        c_s1 = np.sqrt(self.gamma*p_s1/rho_s1)
        c_s2 = np.sqrt(self.gamma*p_s2/rho_s2)
        c_r = np.sqrt(self.gamma*p_r/rho_r)
        if p_l > p_s1:  # 1-rarefaction
            self.velocities.append([
                u_l - c_l, u_s1 - c_s1
            ])
            self.values.append(self._rarefaction_1)
            self.waves.append('rarefaction')
        else:  # 1-shock
            self.velocities.append([
                (rho_s1*u_s1 - rho_l*u_l) / (rho_s1 - rho_l),
                (rho_s1*u_s1 - rho_l*u_l) / (rho_s1 - rho_l),
            ])
            self.values.append(None)
            self.waves.append('shock')
        self.values.append(self.u_star[0])
        self.velocities.append([
            u_s1, u_s2,
        ])
        self.values.append(None)
        self.waves.append('contact')
        self.values.append(self.u_star[1])
        if p_s2 < p_r:  # 3-rarefaction
            self.velocities.append([
                u_s2 + c_s2, u_r + c_r
            ])
            self.values.append(self._rarefaction_3)
            self.waves.append('rarefaction')
        else:  # 3-shock
            self.velocities.append([
                (rho_r*u_r - rho_s2*u_s2) / (rho_r - rho_s2),
                (rho_r*u_r - rho_s2*u_s2) / (rho_r - rho_s2),
            ])
            self.values.append(None)
            self.waves.append('shock')
        self.values.append(self.u_right)

    def _f1(self, p_star):
        """
        Compute the 1-wave that links the left state
        this wave is parametrized by the pressure
        """
        if p_star < 0:
            return np.array([np.nan, np.nan])
        rho_left, u_left, p_left = self.u_left
        facteur = np.sqrt(1-self.mu2**2)/self.mu2
        exposant1 = 1/(2*self.gamma)
        exposant2 = (self.gamma-1)*exposant1
        if p_star < p_left:  # 1-rarefaction
            u_star = u_left - facteur * p_left**exposant1/np.sqrt(rho_left) * (
                p_star**exposant2 - p_left**exposant2
            )
            du_star = - facteur * p_left**exposant1/np.sqrt(rho_left) * (
                exposant2 * p_star**(exposant2-1)
            )
        elif p_star > p_left:  # 1-shock
            u_star = u_left - np.sqrt(
                (1-self.mu2) / rho_left / (p_star+self.mu2*p_left)
            ) * (p_star - p_left)
            du_star = - np.sqrt(
                (1-self.mu2) / rho_left / (p_star+self.mu2*p_left)
            ) * (1 - .5 * (p_star - p_left) / (p_star+self.mu2*p_left))
        else:
            u_star = u_left
            du_star = - facteur * p_left**exposant1/np.sqrt(rho_left) * (
                exposant2 * p_left**(exposant2-1)
            )
        return np.array([u_star, du_star])

    def _f2(self, p_star):
        """
        Compute the 3-wave that links the right state
        this wave is parametrized by the first component p
        """
        if p_star < 0:
            return np.array([np.nan, np.nan])
        rho_right, u_right, p_right = self.u_right
        facteur = np.sqrt(1-self.mu2**2)/self.mu2
        exposant1 = 1/(2*self.gamma)
        exposant2 = (self.gamma-1)*exposant1
        if p_star < p_right:  # 3-rarefaction
            u_star = u_right + facteur*p_right**exposant1/np.sqrt(rho_right)*(
                p_star**exposant2 - p_right**exposant2
            )
            du_star = facteur * p_right**exposant1/np.sqrt(rho_right) * (
                exposant2 * p_star**(exposant2-1)
            )
        elif p_star > p_right:  # 3-shock
            u_star = u_right + np.sqrt(
                (1-self.mu2) / rho_right / (p_star+self.mu2*p_right)
            ) * (p_star - p_right)
            du_star = np.sqrt(
                (1-self.mu2) / rho_right / (p_star+self.mu2*p_right)
            ) * (1 - .5 * (p_star - p_right) / (p_star+self.mu2*p_right))
        else:
            u_star = u_right
            du_star = facteur * p_right**exposant1/np.sqrt(rho_right) * (
                exposant2 * p_right**(exposant2-1)
            )
        return np.array([u_star, du_star])

    def diagram(self):
        pmin = min(
            self.u_left[2],
            self.u_right[2],
            self.u_star[0][2],
        )/100
        pmax = max(
            self.u_left[2],
            self.u_right[2],
            self.u_star[0][2],
        )*2
        v_p = np.linspace(pmin, pmax, 1025)
        # 1-wave
        vu1 = np.zeros(v_p.shape)
        for i, vpi in enumerate(v_p):
            vu1[i] = self._f1(vpi)[0]
        # f1_left, df1_left = self._f1(self.u_left[2])
        # tf1_pmin = f1_left + df1_left * (pmin - self.u_left[2])
        # tf1_pmax = f1_left + df1_left * (pmax - self.u_left[2])
        # 3-wave
        vu2 = np.zeros(v_p.shape)
        for i, vpi in enumerate(v_p):
            vu2[i] = self._f2(vpi)[0]
        # f2_right, df2_right = self._f2(self.u_right[2])
        # tf2_pmin = f2_right + df2_right * (pmin - self.u_right[2])
        # tf2_pmax = f2_right + df2_right * (pmax - self.u_right[2])

        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
        axes.plot(vu1, v_p, color='orange', label='1-wave', alpha=0.5)
        # axes.plot(
        #     [tf1_pmin, tf1_pmax], [pmin, pmax],
        #     color='orange', alpha=0.25
        # )
        axes.plot(vu2, v_p, color='navy', label='3-wave', alpha=0.5)
        # axes.plot(
        #     [tf2_pmin, tf2_pmax], [pmin, pmax],
        #     color='navy', alpha=0.25
        # )
        axes.scatter(self.u_left[1], self.u_left[2],
                     color='orange',
                     s=20,
                     label='left state'
                     )
        axes.scatter(self.u_right[1], self.u_right[2],
                     color='navy',
                     s=20,
                     label='right state'
                     )
        axes.scatter(self.u_star[0][1], self.u_star[0][2],
                     color='red',
                     s=20,
                     label='intermediate states'
                     )
        axes.set_title(type(self).__name__)
        axes.set_xlabel(self.fields[1])
        axes.set_ylabel(self.fields[2])
        axes.legend()
