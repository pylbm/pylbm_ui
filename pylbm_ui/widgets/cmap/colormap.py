import matplotlib.pyplot as plt
import numpy as np

gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))

fig, ax = plt.subplots(figsize=(6, 1))
ax.set_axis_off()

for name in plt.colormaps():
    ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(name))
    plt.savefig(f'{name}.png', dpi=300)

