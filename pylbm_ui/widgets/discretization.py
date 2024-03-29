# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v

from ..config import default_dx
from ..utils import StrictlyPositiveIntField, StrictlyPositiveFloatField, NbPointsField
from .debug import debug


def dx_validity(dx, size):
    """
    Modify dx and the problem size to match.
    """
    n = [round(s/dx) + 1 for s in size]
    L = [(i-1)*dx for i in n]
    return dx, L, n


def n_validity(n, size, i):
    """
    modify n and dx according index i
    """
    ni = n[i]
    dx = size[i] / (ni - 1)
    n = [round(s/dx) + 1 for s in size]
    n[i] = ni
    L = [(i-1)*dx for i in n]
    return dx, L, n


@debug
class DiscretizationWidget(v.ExpansionPanel):
    def __init__(self, test_case_widget, lb_scheme_widget):
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget

        test_case = test_case_widget.get_case()
        lb_param = lb_scheme_widget.parameters
        tc_param = test_case_widget.parameters

        dx = test_case_widget.get_dict_case().get("space_step", default_dx)
        nx = int(test_case.size()[0]/dx) + 1
        if test_case.dim > 1:
            ny = int(test_case.size()[1]/dx) + 1
        else:
            ny = 2
        dt = dx/lb_param['la'].value
        nt = int(test_case.duration/dt)

        self.discret = {
            'nx': NbPointsField(label='Number of points in x', v_model=nx),
            'ny': NbPointsField(
                label='Number of points in y', v_model=ny, class_='d-none'
            ),
            'dx': StrictlyPositiveFloatField(label='Space step', v_model=dx),
            'nt': StrictlyPositiveIntField(
                label='Number of time steps', v_model=nt, disabled=True
            ),
            'dt': StrictlyPositiveFloatField(label='Time step', v_model=dt),
        }
        self.la_vue = v.CardText(children=[lb_param['la']])

        for value in self.discret.values():
            value.observe(self.observer, 'v_model')

        lb_param['la'].observe(self.observer, 'v_model')

        tc_param['xmin'].observe(self.observer, 'v_model')
        tc_param['xmax'].observe(self.observer, 'v_model')
        if test_case.dim > 1:
            tc_param['ymin'].observe(self.observer, 'v_model')
            tc_param['ymax'].observe(self.observer, 'v_model')

        test_case_widget.select_case.observe(self.change_test_case, 'v_model')
        lb_scheme_widget.select_case.observe(self.change_test_case, 'v_model')

        super().__init__(children=[
            v.ExpansionPanelHeader(children=['Discretization']),
            v.ExpansionPanelContent(children=[
                v.Card(children=[
                    v.CardTitle(children=['In space']),
                    v.CardText(children=[
                        self.discret['nx'],
                        self.discret['ny'],
                        self.discret['dx'],
                    ]),
                ], class_="ma-1"),
                v.Card(children=[
                    v.CardTitle(children=['In time']),
                    v.CardText(children=[
                        self.discret['nt'],
                        self.discret['dt'],
                    ]),
                ], class_="ma-1"),
                v.Card(children=[
                    v.CardTitle(children=['Scheme velocity']),
                    self.la_vue,
                ], class_="ma-1"),
            ], class_="px-1"),
        ]),

    def __getitem__(self, i):
        return self.discret[i]

    def observer(self, change):
        test_case = self.test_case_widget.get_case()
        tc_param = self.test_case_widget.parameters
        lb_param = self.lb_scheme_widget.parameters
        # error = lb_param['la'].error
        # for v in self.discret.values():
        #     error |= v.error

        key = None

        if hasattr(change, 'owner'):
            for k, value in self.discret.items():
                if value == change.owner:
                    key = k
                    break

        for value in self.discret.values():
            value.unobserve(self.observer, 'v_model')
        lb_param['la'].unobserve(self.observer, 'v_model')

        problem_size = [tc_param['xmax'].value - tc_param['xmin'].value]
        if 'ymin' in tc_param:
            problem_size.append(
                tc_param['ymax'].value - tc_param['ymin'].value
            )

        duration = test_case.duration

        def fix_values(dx, L, n):
            self.discret['dx'].value = dx
            self.discret['nx'].value = n[0]
            if len(n) > 1:
                self.discret['ny'].value = n[1]

            test_case.set_size(L)
            if not lb_param['la'].error:
                self.discret['dt'].value = self.discret['dx'].value/lb_param['la'].value
                self.discret['nt'].value = duration/self.discret['dt'].value

        if (not self.discret['dx'].error) and (
            key is None or key == 'dx'
        ):
            dx, L, n = dx_validity(self.discret['dx'].value, problem_size)
            fix_values(dx, L, n)
        if (not self.discret['nx'].error) and key == 'nx':
            n = [self.discret['nx'].value]
            if len(problem_size) > 1:
                n.append(
                    self.discret['ny'].value
                )
            dx, L, n = n_validity(n, problem_size, 0)
            fix_values(dx, L, n)
        if (not self.discret['ny'].error) and key == 'ny':
            n = [self.discret['nx'].value]
            if len(problem_size) > 1:
                n.append(
                    self.discret['ny'].value
                )
            dx, L, n = n_validity(n, problem_size, 1)
            fix_values(dx, L, n)
        if (not self.discret['nt'].error) and key == 'nt':
            self.discret['dt'].value = duration/self.discret['nt'].value
            lb_param['la'].value = self.discret['dx'].value/self.discret['dt'].value
        if (not self.discret['dt'].error) and key == 'dt':
            lb_param['la'].value = self.discret['dx'].value/self.discret['dt'].value
            self.discret['nt'].value = duration/self.discret['dt'].value

        for value in self.discret.values():
            value.observe(self.observer, 'v_model')
        lb_param['la'].observe(self.observer, 'v_model')

    def change_test_case(self, change):
        dim = self.test_case_widget.get_case().dim
        if dim == 1:
            self.discret['ny'].class_ = 'd-none'
        else:
            self.discret['ny'].class_ = ''

        tc_param = self.test_case_widget.parameters
        lb_param = self.lb_scheme_widget.parameters
        self.la_vue.children = [lb_param['la']]
        lb_param['la'].observe(self.observer, 'v_model')
        tc_param['xmin'].observe(self.observer, 'v_model')
        tc_param['xmax'].observe(self.observer, 'v_model')
        if dim > 1:
            tc_param['ymin'].observe(self.observer, 'v_model')
            tc_param['ymax'].observe(self.observer, 'v_model')
        dx = self.test_case_widget.get_dict_case().get("space_step", default_dx)
        self.discret['dx'].value = dx
        self.observer(None)
