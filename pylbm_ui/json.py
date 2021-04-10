import json
import os

def save_simu_config(path, filename, dx, test_case, lb_scheme, extra_config=None):
    if not os.path.exists(path):
        os.makedirs(path)

    json.dump(
        {
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