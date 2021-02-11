import pylbm
from typing import Dict, Any
import os
import numpy as np
import matplotlib.pyplot as plt
import io

class Scheme:
    def get_information(self):
        scheme = pylbm.Scheme(self.get_dictionary())
        return scheme

    def get_eqpde(self):
        scheme = pylbm.Scheme(self.get_dictionary())
        eqpde = pylbm.EquivalentEquation(scheme)
        return eqpde

    def get_stability(self, state):
        scheme = pylbm.Scheme(self.get_dictionary())
        stab = pylbm.Stability(scheme)

        stab.is_notebook = True
        stab.visualize(
            {
                'linearization': state,
            }
        )

        return stab

    def get_default_parameters(self, test_case_name):
        print("Test case: {}".format(test_case_name))
        print("""
Proposition of parameters:
    dx =              ??
    scheme_velocity = ??
    s =               ??
       """)


class RelaxationParameter(float):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='number', format='relaxation parameter')

    # @classmethod
    # def __modify_schema__(cls, field_schema):
    #     field_schema.update(
    #         # simplified regex here for brevity, see the wikipedia link above
    #         pattern='^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$',
    #         # some example postcodes
    #         examples=['SP11 9DG', 'w1j7bu'],
    #     )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, float):
            raise TypeError('float required')
        if v < 0 or v > 2:
            raise ValueError('relaxation parameter must be in [0, 2]')
        return cls(v)

    def __repr__(self):
        return f'RelaxationParameter({super().__repr__()})'


def createDirectory(path):
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            return
            #print ("  Directory %s created" % path)








