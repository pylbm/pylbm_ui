import os
import matplotlib

default_path = os.path.join(os.getcwd(), 'Outputs')

plot_config = {
    'linewidth': 2,
    'colors': ['black'],
    'alpha': 0.8,
    'markersize': 10,
    'marker': '.',
    'cmap': matplotlib.cm.RdBu,
    'nan_color': 'black',
}