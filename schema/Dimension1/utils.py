# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import numpy as np


def regularization(x, reg, u_l, u_r):
    y, c = x.copy(), 1
    w = 1-x**2
    z = x.copy()
    for k in range(reg):
        y *= 2*(k+1)
        z *= w
        y += z
        y /= 1+2*(k+1)
        c *= 1+1/(2*(k+1))
    return u_l + .5*(u_r-u_l)*(c*y+1)


def indicator(
    x, reg,
    pos_left=None, pos_right=None,
    width_left=None, width_right=None,
    ub=None, ut=None
):
    """
    initial condition with a regular indicator function

    Parameters
    ----------

    x: ndarray
        spatial mesh
    reg: int
        regularity of the function
    pos_left: float
        position of the left jump
    pos_right: float
        position of the right jump
    width_left: float
        width of the left jump
    width_right: float
        width of the right jump
    ub: float
        bottom value
    ut: float
        top value

    Returns
    -------

    output
        ndarray
    """
    # fix default values for the positions of the jumps
    if pos_left is None:
        pos_left = .75*min(x)+.25*max(x)
    if pos_right is None:
        pos_right = .5*min(x) + .5*max(x)
    # permute the positions if necessary
    if pos_left > pos_right:
        pos_left, pos_right = pos_right, pos_left
        width_left, width_right = width_right, width_left
    # fix default values for the width of the jumps
    if width_left is None:
        width_left = 0.125*(pos_right-pos_left)
    if width_right is None:
        width_right = 0.125*(pos_right-pos_left)
    # rescale the width if necessary
    width_left = abs(width_left)
    width_right = abs(width_right)
    ratio = (pos_right - pos_left) / (width_left + width_right)
    if ratio < 1:
        width_right *= ratio
        width_left *= ratio
    # compute the bounds of each jump
    x_ll, x_lr = pos_left-width_left, pos_left+width_left
    x_rl, x_rr = pos_right-width_right, pos_right+width_right
    output = np.zeros(x.shape) + ub

    if reg < 0:
        ind = np.where(np.logical_and(x < pos_right, x > pos_left))
        output[ind] = ut
    else:
        ind_l = np.where(np.logical_and(x > x_ll, x < x_lr))
        x_sl = 1/width_left*(x[ind_l] - pos_left)
        output[ind_l] = regularization(x_sl, reg, ub, ut)
        ind_m = np.where(np.logical_and(x >= x_lr, x <= x_rl))
        output[ind_m] = ut
        ind_r = np.where(np.logical_and(x > x_rl, x < x_rr))
        x_sr = 1/width_right*(x[ind_r] - pos_right)
        output[ind_r] = regularization(x_sr, reg, ut, ub)

    return output


def bump(x, reg, middle=None, width=None, ub=0, ut=1):
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

    ub: float
        bottom value of the bump

    ut: float
        top value of the bump

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
    output = np.zeros(x.shape) + ub
    ind = np.where(np.logical_and(x < x_right, x > x_left))
    n = reg+1 if reg >= 0 else 0
    output[ind] += (ut - ub) * (
        (x_right - x[ind]) * (x[ind] - x_left)
    )**n / width**(2*n)
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
