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

    def get_stability(self, state, markers1, markers2):
        scheme = pylbm.Scheme(self.get_dictionary())
        # FIXME: remove the output in the notebook by passing a boolean
        #        True if we are in a notebook
        #stab = pylbm.Stability(scheme, True)
        stab = pylbm.Stability(scheme)

        consm0 = [0.] * len(stab.consm)
        for k, moment in enumerate(stab.consm):
            consm0[k] = state.get(moment, 0.)

        n_wv = 1024
        v_xi, eigs = stab.eigenvalues(consm0, n_wv)
        nx = v_xi.shape[1]

        pos0 = np.empty((nx*stab.nvtot, 2))
        for k in range(stab.nvtot):
            pos0[nx*k:nx*(k+1), 0] = np.real(eigs[:, k])
            pos0[nx*k:nx*(k+1), 1] = np.imag(eigs[:, k])
        markers1.set_offsets(pos0)

        pos1 = np.empty((nx*stab.nvtot, 2))
        for k in range(stab.nvtot):
            pos1[nx*k:nx*(k+1), 0] = np.max(v_xi, axis=0)
            pos1[nx*k:nx*(k+1), 1] = np.abs(eigs[:, k])
        markers2.set_offsets(pos1)

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








