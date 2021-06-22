# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v

from .pylbmwidget import out

import sympy as sp
import numpy as np
from traitlets import Unicode, Float, List, Bool

from schema.utils import SchemeVelocity, RelaxationParameterFinal

from .debug import debug
from .dialog_form import Form, Item, Dialog, add_rule
from ..utils import required_fields, FloatField, RelaxField

@debug
class DesignForm(Form):
    def __init__(self, test_case_widget, lb_scheme_widget, discret_widget, **kwargs):
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget
        self.discret_widget = discret_widget
        self.params, self.relax_params = None, None

        self.select_param = v.Select(label='Parameters', v_model=None, items=[])
        self.select_relax = v.Select(label='relaxation rates', v_model=[], items=[], multiple=True, class_='d-none')
        self.srt_relax = v.Switch(label='Single relaxation time', v_model=True, class_='d-none')
        self.sigma = v.Switch(label='Using sigma', v_model=False, class_='d-none')
        self.in_log = v.Switch(label='Using log10', v_model=False, class_='d-none')
        self.minmax = v.Layout()

        self.update_select_fields(None)

        test_case_widget.select_case.observe(self.update_select_fields, 'v_model')
        lb_scheme_widget.select_case.observe(self.update_select_fields, 'v_model')
        discret_widget['dx'].observe(self.update_select_fields, 'v_model')

        self.fields = [self.select_param, self.select_relax, self.srt_relax, self.sigma, self.in_log, self.minmax]

        super().__init__(v_model='valid', children=self.fields)

        self.select_param.observe(self.select_param_changed, 'v_model')
        self.select_relax.observe(self.select_relax_all, 'v_model')
        self.select_relax.observe(self.check_changes, 'v_model')
        self.in_log.observe(self.check_changes, 'v_model')
        self.sigma.observe(self.check_changes, 'v_model')

    def update_select_fields(self, change):
        fields = required_fields(self.test_case_widget.get_case())
        fields.update(required_fields(self.lb_scheme_widget.get_case()))
        fields.update({'dx': {'value': self.discret_widget['dx'].value,
                              'type': 'number'}})

        params = {'relaxation parameters': None}
        params.update({f: v['value'] for f, v in fields.items() if v['type'] != 'relaxation rate'})
        relax_params = {f: v['value'] for f, v in fields.items() if v['type'] == 'relaxation rate'}

        self.params = {k: params[k] for k in sorted(params)}
        self.relax_params = {k: relax_params[k] for k in sorted(relax_params)}

        self.select_param.items = list(self.params.keys())
        self.select_relax.items = ['all'] + list(self.relax_params.keys())

    def select_param_changed(self, change):
        if self.select_param.v_model:
            if self.select_param.v_model == 'relaxation parameters':
                self.minmax.children = [
                    FloatField(label='Enter the minimum', v_model=1),
                    FloatField(label='Enter the maximum', v_model=1)
                ]
                self.select_relax.class_ = ''
                self.srt_relax.class_ = ''
                self.sigma.class_ = ''
                self.in_log.class_ = ''
            else:
                value = self.params[self.select_param.v_model]
                self.minmax.children = [
                    FloatField(label='Enter the minimum', v_model=value),
                    FloatField(label='Enter the maximum', v_model=value)
                ]
                self.select_relax.class_ = 'd-none'
                self.srt_relax.class_ = 'd-none'
                self.sigma.class_ = 'd-none'
                self.in_log.class_ = 'd-none'
                self.select_relax.v_model = []

            for c in self.minmax.children:
                c.observe(self.check_changes, 'v_model')
                c.observe(self.check_changes, 'v_model')

    def select_relax_all(self, change):
        if 'all' in self.select_relax.v_model:
            self.select_relax.v_model = list(self.relax_params.keys())

    @add_rule
    def select_relax_rules(self, change):
        if self.select_param.v_model == 'relaxation parameters':
            if self.select_relax.v_model == []:
                self.select_relax.rules = ['You must select at least one relaxation rate']
                self.select_relax.error = True
                return
            else:
                self.select_relax.rules = []
                self.select_relax.error = False

    @add_rule
    def minmax_rules(self, change):
        if self.minmax.children:
            min_widget, max_widget = self.minmax.children
            min, max = min_widget.value, max_widget.value
            if min == max:
                min_widget.rules = ['Min must be different from Max']
                min_widget.error = True
                max_widget.rules = ['Max must be different from Min']
                max_widget.error = True
                self.minmax.error = True
                return
            elif min > max:
                min_widget.rules = ['Min must be lower than Max']
                min_widget.error = True
                max_widget.rules = ['Max must be greater than Min']
                max_widget.error = True
                self.minmax.error = True
                return
            else:
                min_widget.check(None)
                max_widget.check(None)
                self.minmax.error = min_widget.error | max_widget.error

    @add_rule
    def check_relax_values(self, change):
        if self.minmax.children:
            min_widget, max_widget = self.minmax.children
            min, max = min_widget.value, max_widget.value
            if self.select_param.v_model == 'relaxation parameters':
                if self.sigma.v_model:
                    if not self.in_log.v_model:
                        if min < 0:
                            min_widget.rules = ['Min must be positive']
                            min_widget.error = True
                            self.minmax.error = True
                            return
                        if max < 0:
                            max_widget.rules = ['Max must be positive']
                            max_widget.error = True
                            self.minmax.error = True
                            return
                else:
                    if self.in_log.v_model:
                        if min > np.log10(2):
                            min_widget.rules = [f'Min must be lower than {np.log10(2)}']
                            min_widget.error = True
                            self.minmax.error = True
                            return
                        if max > np.log10(2):
                            max_widget.rules = [f'Max must be lower than {np.log10(2)}']
                            max_widget.error = True
                            self.minmax.error = True
                            return
                    else:
                        if min < 0 or min > 2:
                            min_widget.rules = ['Min must be between 0 and 2']
                            min_widget.error = True
                            self.minmax.error = True
                            return
                        if max < 0 or max > 2:
                            max_widget.rules = ['Max must be between 0 and 2']
                            max_widget.error = True
                            self.minmax.error = True
                            return

    def reset_form(self):
        super().reset_form()
        self.select_relax.class_ = 'd-none'
        self.srt_relax.class_ = 'd-none'
        self.srt_relax.v_model = True
        self.sigma.class_ = 'd-none'
        self.sigma.v_model = False
        self.in_log.class_ = 'd-none'
        self.in_log.v_model = False
        self.minmax.children = []

@debug
class DesignItem(Item):
    form_class = DesignForm
    update_text = 'Update design parameter'

    param = Unicode()
    relax = List()
    srt = Bool()
    sigma = Bool()
    in_log = Bool()
    min = Float()
    max = Float()

    def __init__(self, test_case_widget, lb_scheme_widget, discret_widget, **kwargs):
        super().__init__(test_case_widget, lb_scheme_widget, discret_widget, **kwargs)
        self.content.children = [f'{self}']

    def form2field(self):
        self.param = self.form.select_param.v_model
        self.relax = self.form.select_relax.v_model
        self.srt = self.form.srt_relax.v_model
        self.sigma = self.form.sigma.v_model
        self.in_log = self.form.in_log.v_model
        self.min = self.form.minmax.children[0].value
        self.max = self.form.minmax.children[1].value

    def field2form(self):
        self.form.select_param.v_model = self.param
        self.form.select_relax.v_model = self.relax
        self.form.srt_relax.v_model = self.srt
        self.form.sigma.v_model = self.sigma
        self.form.in_log.v_model = self.in_log
        self.form.minmax.children[0].value =  self.min
        self.form.minmax.children[1].value =  self.max

    def __str__(self):
        if self.param == 'relaxation parameters':
            return ', '.join(self.relax) + f' (srt: {self.srt}, sigma: {self.sigma}, log: {self.in_log}, min: {self.min}, max: {self.max})'
        else:
            return f'{self.param} (min: {self.min}, max: {self.max})'

@debug
class DesignWidget(Dialog):
    item_class = DesignItem
    new_text = "Add new design parameter"

    def __init__(self, test_case_widget, lb_scheme_widget, discret_widget):
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget
        self.discret_widget = discret_widget
        super().__init__(test_case_widget, lb_scheme_widget, discret_widget)

    def create_item(self):
        return DesignItem(self.test_case_widget,
                    self.lb_scheme_widget,
                    self.discret_widget,
                    param = self.form.select_param.v_model,
                    relax = self.form.select_relax.v_model,
                    srt = self.form.srt_relax.v_model,
                    sigma = self.form.sigma.v_model,
                    in_log = self.form.in_log.v_model,
                    min = self.form.minmax.children[0].value,
                    max = self.form.minmax.children[1].value,
                    class_='ma-1',
                    style_='background-color: #F8F8F8;'
        )

    def to_json(self):
        output = []
        for item in self.item_list.children:
            data = {}
            data['param'] = item.param
            data['min'] = item.min
            data['max'] = item.max
            if item.param == 'relaxation parameters':
                data['relax'] = item.relax
                data['srt'] = item.srt
                data['sigma'] = item.sigma
                data['in_log'] = item.in_log
            output.append(data)
        return output

    def design_space(self):
        test_case = self.test_case_widget.get_case()
        lb_scheme = self.lb_scheme_widget.get_case()
        discret = self.discret_widget

        output = {}
        for c in self.item_list.children:
            if c.relax:
                attrs = [getattr(lb_scheme, r).symb for r in c.relax]

                if c.srt:
                    output.update({tuple(attrs): (c.min, c.max)})
                else:
                    output.update({a: (c.min, c.max) for a in attrs})
            else:
                if c.param == 'dx':
                    output.update({'dx': (c.min, c.max)})
                else:
                    if hasattr(test_case, c.param):
                        attr = getattr(test_case, c.param)
                    elif hasattr(lb_scheme, c.param):
                        attr = getattr(lb_scheme, c.param)
                        if isinstance(attr, SchemeVelocity):
                            attr = attr.symb
                    if not isinstance(attr, sp.Symbol):
                        attr = c.param
                    output.update({attr: (c.min, c.max)})
        return output

    def transform_design_space(self, sample):
        test_case = self.test_case_widget.get_case()
        lb_scheme = self.lb_scheme_widget.get_case()
        discret = self.discret_widget

        def update(i, c):
            if c.in_log:
                sample[i] = 10**sample[i]
            if c.sigma:
                sample[i] = 2./(2.*sample[i] + 1.)

        ic = 0
        for c in self.item_list.children:
            if c.param == 'relaxation parameters':
                if c.srt:
                    update(ic, c)
                    ic += 1
                else:
                    for r in c.relax:
                        update(ic, c)
                        ic += 1
            else:
                ic += 1
