import numpy as np
import matplotlib.pyplot as plt

xmin, xmax = -1.5, 1.5
x = np.linspace(xmin, xmax, 1000)
y = np.zeros(x.shape)
ind_in = np.logical_and(x > -1, x < 1)
x_in = x[ind_in]

fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(1, 1, 1)

# n = -1
y[ind_in] = 1
ax.plot(x, y, linewidth=2, color='black', label=r'$n=-1$')

for n in range(1, 4):
    y[ind_in] = (1-x_in**2)**n
    ax.plot(x, y, linewidth=2, color=(0, n/4, 1-n/4), label=f'$n={n-1}$')

ax.grid(False)
ax.set_title("Several bump functions", fontsize=24)
ax.legend()
ax.set_xticks([-1, 0, 1])
ax.set_xticklabels([r'$x_b-\ell$', r'$x_b$', r'$x_b+\ell$'], fontsize=15)
ax.set_yticks([0, 1])
ax.set_yticklabels([r'$\rho_g$', r'$\rho_b$'], fontsize=15)

fig.savefig("image_bump.png")