# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import os
import ipyvuetify as v
import numpy as np
import copy
import pylbm

from .pylbmwidget import out

from .. import responses as pylbm_responses
from schema.utils import RelaxationParameterFinal

class CFL:
    def __init__(self, test_case):
        eq = test_case.equation
        if hasattr(eq, 'rho'):
            self.rho = eq.rho
            if test_case.dim == 1:
                self.vel = [eq.q]
            elif test_case.dim == 2:
                self.vel = [eq.qx, eq.qy]
        else:
            self.rho = None

    def __call__(self, path, test_case, simu_cfg):
        if self.rho:
            return pylbm_responses.CFL(self.rho, self.vel)
        else:
            return None

    def __str__(self):
        return 'CFL'

class Error:
    def __init__(self, field, expr, relative=False, log10=True):
        self.field = field
        self.expr = expr
        self.relative = relative
        self.log10 = log10

    def __call__(self, path, test_case, simu_cfg):
            domain = pylbm.Domain(simu_cfg)
            time_e = test_case.duration
            ref = test_case.ref_solution(time_e, domain.x, field=self.field)

            return pylbm_responses.Error(ref, self.expr, log10=self.log10, relative=self.relative)

    def __str__(self):
        return f'err_{self.field}'

class Plot:
    def __init__(self, field, expr):
        self.field = field
        self.expr = expr

    def __call__(self, path, test_case, simu_cfg):
            ref = None
            if hasattr(test_case, 'ref_solution'):
                domain = pylbm.Domain(simu_cfg)
                time_e = test_case.duration
                ref = test_case.ref_solution(time_e, domain.x, field=self.field)

            return pylbm_responses.Plot(os.path.join(path, f'{self.field}.png'), self.expr, ref)

def build_responses_list(test_case, lb_scheme):
    responses = {'linear stability': pylbm_responses.LinearStability(test_case.state()),
                 'CFL': CFL(test_case),
    }

    fields = test_case.equation.get_fields()
    for name, expr in fields.items():
        responses[f'plot {name}'] = Plot(name, expr)
        if hasattr(test_case, 'ref_solution'):
            # responses[f'stability on {name}'] = pylbm_responses.Stability(expr)
            responses[f'log of error on {name}'] = Error(name, expr)
            responses[f'log of error avg on {name}'] = pylbm_responses.ErrorAvg(name, test_case.ref_solution, expr)
            responses[f'log of error std on {name}'] = pylbm_responses.ErrorStd(name, test_case.ref_solution, expr)
            responses[f'log of relative error on {name}'] = Error(name, expr, relative=True)

    def add_relax(v):
        responses[k] = pylbm_responses.S(v.symb)
        responses[f'sigma for {k}'] = pylbm_responses.Sigma(v.symb)
        responses[f'log of sigma for {k}'] = pylbm_responses.Sigma(v.symb, log10=True)
        responses[f'diff for {k}'] = pylbm_responses.Diff(v.symb)
        responses[f'log of diff for {k}'] = pylbm_responses.Diff(v.symb, log10=True)
        responses[f'diff/dx for {k}'] = pylbm_responses.Diff(v.symb, with_dx=False)
        responses[f'log of diff/dx for {k}'] = pylbm_responses.Diff(v.symb, with_dx=False, log10=True)

    for k, v in lb_scheme.__dict__.items():
        if isinstance(v, RelaxationParameterFinal):
            add_relax(v)

    return responses

class ResponsesWidget:
    def __init__(self, test_case_widget, lb_scheme_widget):

        self.responses = {}

        self.responses_list = v.Select(label='Responses', v_model=[], items=[], multiple=True)


        def update_responses(change):
            test_case = test_case_widget.get_case()
            lb_scheme = lb_scheme_widget.get_case()

            self.responses = build_responses_list(test_case, lb_scheme)

            self.responses_list.items = ['all'] + list(self.responses.keys())

        def select_all(change):
            if 'all' in self.responses_list.v_model:
                self.responses_list.v_model = list(self.responses.keys())

        update_responses(None)

        self.responses_list.observe(select_all, 'v_model')

        test_case_widget.select_case.observe(update_responses, 'v_model')
        lb_scheme_widget.select_case.observe(update_responses, 'v_model')
        self.widget = self.responses_list

    def get_list(self, path, test_case, simu_cfg):
        output = []
        for v in self.responses_list.v_model:
            if isinstance(self.responses[v], (pylbm_responses.FromConfig,
                                              pylbm_responses.DuringSimulation,
                                              pylbm_responses.AfterSimulation,)):
                output.append(copy.deepcopy(self.responses[v]))
            else:
                output.append(copy.deepcopy(self.responses[v](path, test_case, simu_cfg)))
        return output
