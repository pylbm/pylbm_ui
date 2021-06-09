# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
import pylbm
from typing import Dict, Any
import os
import numpy as np
import matplotlib.pyplot as plt
import io
from pydantic import BaseModel
from pydantic.utils import Representation
from pydantic.json import ENCODERS_BY_TYPE

import numbers
import sympy as sp
from copy import deepcopy

from pathlib import Path
from pkgutil import iter_modules
from importlib import import_module


def define_cases(filename, modulename):
    """
    return the cases and known_cases of the local submodules

    Parameters
    ----------
    filename: string
    modulename: string

    Returns
    -------

    cases: dictionary
        the cases of the submodules
    """
    cases = {}
    gbl = globals()
    package_dir = Path(filename).resolve().parent
    for _, module_name, ispkg in iter_modules([package_dir]):
        if ispkg:
            module = f"{modulename}.{module_name}"
            gbl['md'] = import_module(module, package=None)
            cases[module_name] = md.cases
    return cases


def freeze(d):
    if isinstance(d, dict):
        return frozenset((key, freeze(value)) for key, value in d.items())
    elif isinstance(d, list):
        return tuple(freeze(value) for value in d)
    return d


class HashBaseModel(BaseModel):
    default_values = {}
    description_file = 'none'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # duplicate the initial parameters to default_parameters
        # This default_parameters are used to restart the scheme
        self.default_values = kwargs

    def __hash__(self):
        set = frozenset((type(self),))
        set.union(freeze(self.__dict__))
        return hash(set)

    @property
    def description(self):
        import os
        import inspect

        full_path = inspect.getfile(self.__class__)
        path = os.path.dirname(full_path)

        if self.description_file != 'none':
            html_filename = os.path.join(path, self.description_file)
        else:
            class_name = self.__class__.__name__.lower()
            html_filename = os.path.join(path, f'{class_name}.html')

        if os.path.exists(html_filename):
            return open(html_filename).read()

        return ''
class Scheme:
    def get_information(self):
        scheme = pylbm.Scheme(self.get_dictionary())
        return scheme

    def get_required_param(self):
        return []

    def get_eqpde(self):
        scheme = pylbm.Scheme(self.get_dictionary())
        eqpde = pylbm.EquivalentEquation(scheme)
        return eqpde

    def get_stability(self, state, markers1=None, markers2=None):
        dico = deepcopy(self.get_dictionary())
        param = self.get_required_param()
        for p in param:
            dico['parameters'][p] = state[p]
        scheme = pylbm.Scheme(dico)
        stab = pylbm.Stability(scheme)

        consm0 = [0.] * len(stab.consm)
        for k, moment in enumerate(stab.consm):
            consm0[k] = state.get(moment, 0.)

        n_wv = 1024
        v_xi, eigs = stab.eigenvalues(consm0, n_wv)
        nx = v_xi.shape[1]

        if markers1 is not None:
            pos0 = np.empty((nx*stab.nvtot, 2))
            for k in range(stab.nvtot):
                pos0[nx*k:nx*(k+1), 0] = np.real(eigs[:, k])
                pos0[nx*k:nx*(k+1), 1] = np.imag(eigs[:, k])
            markers1.set_offsets(pos0)

        if markers2 is not None:
            pos1 = np.empty((nx*stab.nvtot, 2))
            for k in range(stab.nvtot):
                pos1[nx*k:nx*(k+1), 0] = np.max(v_xi, axis=0)
                pos1[nx*k:nx*(k+1), 1] = np.abs(eigs[:, k])
            markers2.set_offsets(pos1)

        return stab


class SchemeVelocity(Representation):
    def __init__(self, value):
        self.symb = sp.symbols('lambda')
        self.value = value

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='number', format='scheme velocity')

    @classmethod
    def validate(cls, v):
        if not isinstance(v, numbers.Number):
            raise TypeError('number required')
        if v < 0:
            raise ValueError('strictly positive number required')
        return cls(v)

    def __str__(self):
        return self.value

    def __repr_args__(self):
        return [(None, self.value), ['symbol', self.symb]]


class RelaxationParameter:
    def __new__(cls, symb):
        class Create:
            def __new__(self, v):
                return RelaxationParameterFinal(v, sp.Symbol(symb))

            @classmethod
            def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
                field_schema.update(type='number', format='relaxation parameter')

            @classmethod
            def __get_validators__(cls):
                yield cls.validate

            @classmethod
            def validate(cls, v):
                if not isinstance(v, numbers.Number):
                    raise TypeError('Number is required')
                if v < 0 or v > 2:
                    raise ValueError('relaxation parameter must be in [0, 2]')
                return cls(v)

        return Create


class RelaxationParameterFinal:
    def __init__(self, value, symb):
        self.symb = symb
        self.value = value

    def __repr__(self):
        return f"RelaxationParameter('{self.symb}')({self.value})"


class RealParameter:
    def __new__(cls, symb):
        class Create:
            def __new__(self, v):
                return RealParameterFinal(v, sp.Symbol(symb))

            @classmethod
            def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
                field_schema.update(type='number', format='parameter')

            @classmethod
            def __get_validators__(cls):
                yield cls.validate

            @classmethod
            def validate(cls, v):
                if not isinstance(v, numbers.Number):
                    raise TypeError('Number is required')
                return cls(v)

        return Create


class RealParameterFinal:
    def __init__(self, value, symb):
        self.symb = symb
        self.value = value

    def __repr__(self):
        return f"Parameter('{self.symb}')({self.value})"


class LBM_scheme(HashBaseModel, Scheme):
    la: SchemeVelocity


ENCODERS_BY_TYPE.update({
    SchemeVelocity: lambda o: o.value,
    RelaxationParameterFinal: lambda o: o.value,
    RealParameterFinal: lambda o: o.value,
    })
