# from .Euler import cases, known_cases

from pathlib import Path
from pkgutil import iter_modules
from importlib import import_module


cases = {}
known_cases = {}
gbl = globals()
package_dir = Path(__file__).resolve().parent

for _, module_name, ispkg in iter_modules([package_dir]):
    if ispkg:
        module = f"{__name__}.{module_name}"
        gbl['md'] = import_module(module, package=None)
        cases.update(md.cases)
        known_cases.update(md.known_cases)
