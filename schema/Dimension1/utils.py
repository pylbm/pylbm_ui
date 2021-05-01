# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import numpy as np


def bump(x, reg, middle=None, width=None):
    """
    initial condition with a bump

    Parameters
    ----------

    x: ndarray
        spatial mesh
    
    reg: int
        regularity of the function

    middle: float
        position of the top of the bump

    width: float
        width of the bump

    Returns
    -------

    output
        ndarray
    """
    if middle is None:
        middle = .75*min(x)+.25*max(x)
    if width is None:
        width = 0.125*(max(x)-min(x))
    x_left, x_right = middle-width, middle+width
    output = np.zeros(x.shape)

    ind_l = np.where(np.logical_and(x > x_left, x <= middle))
    ind_r = np.where(np.logical_and(x < x_right, x > middle))
    x_sl = (x[ind_l] - x_left - 0.5*width) / (0.5*width)
    x_sl_k = np.copy(x_sl)
    x_sl *= x_sl
    x_sr = (x[ind_r] - middle - 0.5*width) / (0.5*width)
    x_sr_k = np.copy(x_sr)
    x_sr *= x_sr

    def binomial(n, k):
        if 0 <= k <= n:
            ntok = 1
            ktok = 1
            for t in range(1, min(k, n - k) + 1):
                ntok *= n
                ktok *= t
                n -= 1
            return ntok // ktok
        else:
            return 0

    cte = 0.
    for k in range(reg+1):
        coeff = (-1)**k * binomial(reg, k) / (2*k+1)
        output[ind_l] += coeff * x_sl_k
        output[ind_r] -= coeff * x_sr_k
        cte += coeff
        x_sl_k *= x_sl
        x_sr_k *= x_sr
    output[ind_l] += cte
    output[ind_r] += cte
    output /= 2*cte
    return output


def riemann_pb(x, xmid, u_left, u_right):
    """
    initial condition with a Riemann problem

    Parameters
    ----------

    x : ndarray
        spatial mesh

    xmid : double
        position of the discontinuity

    u_left : double
        left value of the field

    u_right : double
        right value of the field

    Returns
    -------

    vect_u
        ndarray
    """
    vect_u = np.empty(x.shape)
    vect_u[x < xmid] = u_left
    vect_u[x >= xmid] = u_right
    return vect_u
