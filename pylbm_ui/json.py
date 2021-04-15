# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import json
import os

def save_simu_config(path, filename, dx, test_case, lb_scheme, extra_config=None):
    if not os.path.exists(path):
        os.makedirs(path)

    json.dump(
        {
            'dim': lb_scheme.dim,
            'dx': dx,
            'test_case': {
                'module': test_case.__module__,
                'class': test_case.__class__.__name__,
                'args': json.loads(test_case.json(skip_defaults=True)),
            },
            'lb_scheme': {
                'module': lb_scheme.__module__,
                'class': lb_scheme.__class__.__name__,
                'args': json.loads(lb_scheme.json(skip_defaults=True)),
            },
            'extra_config': extra_config,
        },
        open(os.path.join(path, filename), 'w'),
        sort_keys=True,
        indent=4,
    )

def save_param_study_for_simu(path, filename, design, responses):
    if not os.path.exists(path):
        os.makedirs(path)

    json.dump(
        {
            'design_space': design,
            'responses': responses,
        },
        open(os.path.join(path, filename), 'w'),
        sort_keys=True,
        indent=4,
    )