import os
import copy
import matplotlib

default_path = os.path.join(os.getcwd(), 'Outputs')

plot_config = {
    'linewidth': 2,
    'linestyle': '-',
    'colors': ['#000000'],
    'alpha': 0.8,
    'markersize': 10,
    'marker': '.',
    'cmap': copy.copy(matplotlib.cm.get_cmap("RdBu")),
    'nan_color': 'black',
}