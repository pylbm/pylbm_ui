# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
import sympy as sp
from pydantic.json import ENCODERS_BY_TYPE
from typing import Dict, Any

class Symbol(sp.Symbol):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='string', format='sympy symbol')

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('SymPy Symbol required')
        return sp.Symbol(v)

    def __repr__(self):
        return super().__repr__()

ENCODERS_BY_TYPE[Symbol] = str
ENCODERS_BY_TYPE[sp.Symbol] = str