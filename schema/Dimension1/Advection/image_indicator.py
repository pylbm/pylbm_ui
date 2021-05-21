import numpy as np
import matplotlib.pyplot as plt


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

#############################
# P_n
#############################
xmin, xmax = -1, 1
x = np.linspace(xmin, xmax, 1000)

fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(1, 1, 1)

for n in range(4):
    y = regularization(x, n, -1, 1)
    ax.plot(
        x, y,
        linewidth=2, color=(0, n/4, 1-n/4),
        alpha=0.5, label=f'$n={n}$'
    )

ax.grid(True)
ax.set_title(r"Several $P_n$ functions", fontsize=24)
ax.legend()
ax.set_xticks([-1, 0, 1])
ax.set_xticklabels([r'$x_b-\ell$', r'$x_b$', r'$x_b+\ell$'], fontsize=15)
ax.set_yticks([-1, 1])
ax.set_yticklabels(["-1", "1"], fontsize=15)

fig.savefig("image_indicator_Pn.png")

#############################
# indicator function
#############################
xmin, xmax = -2, 2
pos_left, pos_right = -1, 1
width_left, width_right = 0.5, 0.5
x_ll, x_lr = pos_left-width_left, pos_left+width_left
x_rl, x_rr = pos_right-width_right, pos_right+width_right

x = np.linspace(xmin, xmax, 1000)
y = np.zeros(x.shape)

fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(1, 1, 1)

for n in range(4):
    ind_l = np.where(np.logical_and(x > x_ll, x < x_lr))
    x_sl = 1/width_left*(x[ind_l] - pos_left)
    y[ind_l] = regularization(x_sl, n, 0, 1)
    ind_m = np.where(np.logical_and(x >= x_lr, x <= x_rl))
    y[ind_m] = 1
    ind_r = np.where(np.logical_and(x > x_rl, x < x_rr))
    x_sr = 1/width_right*(x[ind_r] - pos_right)
    y[ind_r] = regularization(x_sr, n, 1, 0)
    ax.plot(
        x, y,
        linewidth=2, color=(0, n/4, 1-n/4), 
        alpha=0.5, label=f'$n={n}$'
    )

ax.grid(True)
ax.set_title(r"Several indicator functions", fontsize=24)
ax.legend()
ax.set_xticks([
    pos_left-width_left, pos_left+width_left,
    pos_right-width_right, pos_right+width_right
])
ax.set_xticklabels([
    r'$x_l-d_l$', r'$x_l+d_l$',
    r'$x_r-d_r$', r'$x_r+d_r$'
], fontsize=15)
ax.set_yticks([0, 1])
ax.set_yticklabels([
    r'$u_{out}$', r'$u_{in}$'
], fontsize=15)

fig.savefig("image_indicator.png")

plt.show()