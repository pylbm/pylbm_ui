# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import json
import os
from .widgets.debug import debug_func

@debug_func
def save_simu_config(path, filename, dx, model, test_case, lb_scheme, extra_config=None, responses=None):
    if not os.path.exists(path):
        os.makedirs(path)

    json.dump(
        {
            'dim': lb_scheme.dim,
            'dx': dx,
            'v_model': model,
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
            'responses': responses,
        },
        open(os.path.join(path, filename), 'w'),
        sort_keys=True,
        indent=4,
    )

@debug_func
def save_param_study(path, filename, dx, model, test_case, lb_scheme, param_widget, sampling):
    if not os.path.exists(path):
        os.makedirs(path)

    samples = {}
    design = param_widget.design.design_space().keys()
    for isample, sample in enumerate(sampling):
        samples[isample] = {str(d): s for d, s in zip(design, sample)}

    json.dump(
        {
            'dim': lb_scheme.dim,
            'dx': dx,
            'v_model': model,
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
            'design_space': param_widget.design.to_json(),
            'responses': param_widget.responses.responses_list.v_model,
            'sampling_method': param_widget.sampling_method.v_model,
            'sample_size': param_widget.sample_size.v_model,
            'sampling': samples
        },
        open(os.path.join(path, filename), 'w'),
        sort_keys=True,
        indent=4,
    )

@debug_func
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

@debug_func
def save_stats(path, filename, stats):
    if not os.path.exists(path):
        os.makedirs(path)

    json_data = {}

    file = os.path.join(path, filename)
    if os.path.exists(file):
        json_data = json.load(open(file, 'r'))

    json_data['stats'] = stats
    json.dump(
        json_data,
        open(file, 'w'),
        sort_keys=True,
        indent=4,
    )
