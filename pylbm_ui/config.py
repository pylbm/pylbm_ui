# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import os
import copy
import matplotlib

default_path = os.path.join(os.getcwd(), 'Outputs')
voila_notebook = os.getcwd()

plot_config = {
    'linewidth': 2,
    'linestyle': '-',
    'colors': ['#000000'],
    'alpha': 0.8,
    'markersize': 10,
    'marker': '.',
    'cmap': "RdBu",
    'nan_color': 'black',
}

# for simulation
nb_split_period = 10
default_dx = 0.005