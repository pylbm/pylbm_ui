# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

from functools import wraps
import inspect

from .pylbmwidget import out

def get_subclass_methods(child_cls):
    parents = inspect.getmro(child_cls)[1:]
    parents_methods = set()
    for parent in parents:
        members = inspect.getmembers(parent, predicate=inspect.isfunction)
        parents_methods.update(members)

    child_methods = set(inspect.getmembers(child_cls, predicate=inspect.isfunction))

    return child_methods - parents_methods

def debug_func(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with out:
            result = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                result = e
                raise

    return wrapper

def debug(klass):
    for entry in get_subclass_methods(klass):
        key, value = entry
        wrapped = debug_func(value)
        setattr(klass, key, wrapped)
    return klass