import ipyvuetify as v
import numpy as np
import pylbm

from .pylbmwidget import out

from .. import responses as pylbm_responses
from schema.utils import RelaxationParameterFinal

def CFL(test_case):
    eq = test_case.equation
    if test_case.dim == 1:
        vel = [eq.q]
    elif test_case.dim == 2:
        vel = [eq.qx, eq.qy]

    return pylbm_responses.CFL(eq.rho, vel)

def Error(field, expr, test_case, simu_cfg, relative=False):
    domain = pylbm.Domain(simu_cfg)
    time_e = test_case.duration
    ref = test_case.ref_solution(time_e, domain.x, field=field)

    return pylbm_responses.Error(ref, expr, log10=False, relative=relative)

class Responses_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):

        self.responses = {}

        self.responses_list = v.Select(label='Responses', v_model=[], items=[], multiple=True)

        def update_responses(change):
            self.responses = {'linear stability': lambda test_case, simu_cfg: pylbm_responses.LinearStability(test_case.state()),
                              'CFL': lambda test_case, simu_cfg: CFL(test_case),
            }

            test_case = test_case_widget.get_case()
            lb_case = lb_scheme_widget.get_case()

            if hasattr(test_case, 'ref_solution'):
                fields = test_case.equation.get_fields()
                for name, expr in fields.items():
                    self.responses[f'error on {name}'] = lambda test_case, simu_cfg: Error(name, expr, test_case, simu_cfg)
                    self.responses[f'relative error on {name}'] = lambda test_case, simu_cfg: Error(name, expr, test_case, simu_cfg, True)

            def add_relax(v):
                self.responses[k] = lambda test_case, simu_cfg: pylbm_responses.S(v.symb)
                self.responses[f'sigma for {k}'] = lambda test_case, simu_cfg: pylbm_responses.Sigma(v.symb)
                self.responses[f'diff for {k}'] = lambda test_case, simu_cfg: pylbm_responses.Diff(v.symb)
                self.responses[f'diff with dx=1 for {k}'] = lambda test_case, simu_cfg: pylbm_responses.Diff(v.symb, with_dx=False)

            for k, v in lb_case.__dict__.items():
                if isinstance(v, RelaxationParameterFinal):
                    print('v', v)
                    add_relax(v)

            self.responses_list.items = list(self.responses.keys())

        update_responses(None)
        test_case_widget.select_case.observe(update_responses, 'v_model')
        lb_scheme_widget.select_case.observe(update_responses, 'v_model')
        self.widget = self.responses_list

    def get_list(self, test_case, simu_cfg):
        return [self.responses[v](test_case, simu_cfg) for v in self.responses_list.v_model]