# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
from pydantic import BaseModel
from pydantic.utils import  Representation

from .utils import HashBaseModel

class Interval(list):
    def __init__(self, bounds):
        super().__init__(bounds)
        # self.bounds = bounds

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='array', format='interval')

    @classmethod
    def validate(cls, v):
        if not isinstance(v, list):
            raise TypeError('list required')
        if len(v) != 2:
            raise ValueError('List of two floats required')
        return cls(v)

    def __str__(self):
        return self.bounds

    def size(self):
        return self[1] - self[0]

class Domain1D(HashBaseModel):
    x: Interval

    @property
    def size(self):
        return [self.x.size()]

class Domain2D(Domain1D):
    y: Interval

    @property
    def size(self):
        return [self.x.size(), self.y.size()]

