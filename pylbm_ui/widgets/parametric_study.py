# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v
import os
import markdown
import plotly.graph_objects as go
import numpy as np
from skopt.sampler import Lhs, Sobol, Halton, Hammersly
import copy
import pylbm
import tempfile
import shutil
import asyncio
import pathos
import pathos.pools as pp

from .debug import debug
from .design_space import DesignWidget
from .dialog_path import DialogPath
from .discretization import dx_validity
from .responses import ResponsesWidget
from ..config import default_path
from ..responses import FromConfig, DuringSimulation, AfterSimulation
from ..simulation import simulation, get_config
from ..utils import required_fields
from ..json import save_simu_config, save_param_study_for_simu
from .message import Message

def run_simulation(args):
    simu_cfg, sample, duration, responses = args
    simu_cfg['codegen_option']['generate'] = False

    output = [0]*len(responses)

    sol = pylbm.Simulation(simu_cfg, initialize=False)
    sol.extra_parameters = sample

    sol._need_init = True
    solid_cells = sol.domain.in_or_out != sol.domain.valin

    for i, r in enumerate(responses):
        if isinstance(r, FromConfig):
            output[i] = r(simu_cfg, sample)

    def test_nan():
        c = list(sol.scheme.consm.keys())[0]
        sol.m_halo[c][solid_cells] = 0
        data = sol.m[c]
        if np.isnan(np.sum(data)) or np.any(np.abs(data)>1e20):
            return True
        return False

    actions = [r for r in responses if isinstance(r, DuringSimulation)]

    nan_detected = False
    nite = 0
    while sol.t <= duration and not nan_detected:
        sol.one_time_step()

        for a in actions:
            a(sol)

        if nite == 200:
            nite = 0
            nan_detected = test_nan()
        nite += 1

    nan_detected |= test_nan()

    for i, r in enumerate(responses):
        if isinstance(r, AfterSimulation):
            output[i] = r(sol)
        elif isinstance(r, DuringSimulation):
            output[i] = r.value()


    return [not nan_detected] + output

skopt_method = {'Latin hypercube': Lhs,
                'Sobol': Sobol,
                'Halton': Halton,
                'Hammersly': Hammersly,
}

@debug
class ParametricStudyWidget:
    def __init__(self, test_case_widget, lb_scheme_widget, discret_widget):
        """
        Widget definition for parametric study of lattice Boltzmann methods.

        Parameters
        ==========

        - test_case_widget:
            widget of the test case (see test_case.py).

        - lb_scheme_widget:
            widget of the lattice Boltzmann scheme (see lb_scheme.py).

        This widget is composed by a menu where you can define the design space of the parametric study,
        the responses computed on each sample and the method used to generate the sampling as well as
        the number of points.

        This widget is also composed by a main widget where the result of the parametric study is
        represented by a parallel coordinates plot using plotly.

        """
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget
        self.discret_widget = discret_widget
        self.tmp_dir = tempfile.TemporaryDirectory()

        ##
        ## The menu
        ##
        self.study_name = v.TextField(label='Study name', v_model='PS_0')

        # self.space_step = v.TextField(label='Space step', v_model=0.01, type='number')
        self.codegen = v.Select(label='Code generator', items=['auto', 'numpy', 'cython'], v_model='auto')

        self.design = DesignWidget(test_case_widget, lb_scheme_widget, discret_widget)
        self.responses = ResponsesWidget(test_case_widget, lb_scheme_widget)

        self.sampling_method = v.Select(label='Method', items=list(skopt_method.keys()), v_model=list(skopt_method.keys())[0])
        self.sample_size = v.TextField(label='Number of samples', v_model=10, type='number')

        self.run = v.Btn(v_model=True, children=['Run parametric study'], class_="ma-5", color='success')

        self.menu = [
            self.study_name,
            # self.space_step,
            self.codegen,
            v.ExpansionPanels(children=[
                v.ExpansionPanel(children=[
                    v.ExpansionPanelHeader(children=['Design space']),
                    v.ExpansionPanelContent(children=[self.design.widget]),
                ]),
                v.ExpansionPanel(children=[
                    v.ExpansionPanelHeader(children=['Responses']),
                    v.ExpansionPanelContent(children=[self.responses.widget]),
                ]),
                v.ExpansionPanel(children=[
                    v.ExpansionPanelHeader(children=['Sampling method']),
                    v.ExpansionPanelContent(children=[self.sampling_method, self.sample_size]),
                ]),
            ], multiple=True),
            v.Row(children=[self.run], align='center', justify='center'),
        ]

        ##
        ## The main
        ##
        self.dialog = DialogPath()
        self.plotly_plot = v.Container(align_content_center=True)
        self.main = [v.Row(children=[self.plotly_plot]), self.dialog]

        ##
        ## Widget events
        ##
        self.run.on_event('click', self.start_PS)
        self.test_case_widget.select_case.observe(self.purge, 'v_model')
        self.lb_scheme_widget.select_case.observe(self.purge, 'v_model')
        self.codegen.observe(self.purge, 'v_model')

    def start_PS(self, widget, event, data):
        if self.run.v_model:
            path = os.path.join(default_path, self.study_name.v_model)
            self.dialog.check_path(path)

            asyncio.ensure_future(self.run_study(path))
            # self.run_study(path)
        else:
            self.stop_simulation(None)

    async def run_study(self, path):
    # def run_study(self, path):
        """
        Create the sampling using the design space defined in the menu and start the
        parametric study on each sample.
        Then the results is represented by plotly.
        """
        while self.dialog.v_model:
            await asyncio.sleep(0.01)

        if not self.dialog.replace:
            self.stop_simulation(None)
            return

        try:
            shutil.rmtree(self.tmp_dir.name)
        except OSError:
            # Could be some issues on Windows
            pass

        design_space = self.design.design_space()
        if design_space:
            self.run.v_model = False
            self.run.children = ['Stop parametric study']
            self.run.color = 'error'

            dx = self.discret_widget['dx'].value
            test_case = copy.deepcopy(self.test_case_widget.get_case())
            lb_scheme = copy.deepcopy(self.lb_scheme_widget.get_case())

            message = Message('Initialize')
            self.plotly_plot.children = [message]
            sampling = np.asarray(skopt_method[self.sampling_method.v_model]().generate(list(design_space.values()), int(self.sample_size.v_model)))

            message.update(f'Prepare the simulation in {self.tmp_dir.name}')
            simu = simulation()
            simu.reset_sol(test_case, lb_scheme, dx, self.codegen.v_model, exclude=design_space.keys(), initialize=False, codegen_dir=self.tmp_dir.name, show_code=False)

            args = []
            tmp_case = test_case.copy()
            for i, s in enumerate(sampling):
                design_sample = {}

                for ik, k in enumerate(design_space.keys()):
                    if k in test_case.__dict__:
                        setattr(test_case, k, s[ik])
                    else:
                        if isinstance(k, tuple):
                            for kk in k:
                                design_sample[kk] = s[ik]
                        else:
                            design_sample[k] = s[ik]

                if 'dx' in design_sample:
                    dx = design_sample['dx']
                    dx, L, _ = dx_validity(dx, test_case.size())
                    design_sample['dx'] = dx
                    test_case.set_size(L)

                la = lb_scheme.la.value
                if lb_scheme.la.symb in design_sample:
                    la = design_sample[lb_scheme.la.symb]
                dt = dx/la

                duration = test_case.duration
                if 'duration' in design_sample:
                    duration = design_sample['duration']

                tmp_case.duration = np.floor(test_case.duration/dt)*dt
                if tmp_case.duration%dt != 0:
                    tmp_case.duration += dt

                simu_path = os.path.join(path, f'simu_{i}')
                simu_cfg = get_config(tmp_case, lb_scheme, dx, self.codegen.v_model, exclude=design_space.keys(), codegen_dir=self.tmp_dir.name)
                save_simu_config(simu_path, 'simu_cfg.json', dx, tmp_case, lb_scheme, {str(k): v for k, v in design_sample.items()})
                args.append((simu_cfg, design_sample, tmp_case.duration, self.responses.get_list(simu_path, tmp_case, simu_cfg)))

            message.update('Run simulations on the sampling...')

            def run_parametric_study():
                from pathos.multiprocessing import ProcessingPool
                pool = pp.ProcessPool()
                output = pool.map(run_simulation, args)

                dimensions = [dict(values=np.asarray([o[0] for o in output], dtype=np.float64), label='stability')]

                dimensions.extend([dict(values=sampling[:, ik], label=f'{k}') for ik, k in enumerate(design_space.keys())])

                for i, r in enumerate(self.responses.widget.v_model):
                    if output[0][i+1] is not None:
                        dimensions.append(dict(values=np.asarray([o[i+1] for o in output], dtype=np.float64), label=r))

                for isamp in range(len(sampling)):
                    tmp_design = {f'{k}': sampling[isamp, ik] for ik, k in enumerate(design_space.keys())}
                    tmp_responses = {r: output[isamp][ir + 1] for ir, r in enumerate(self.responses.widget.v_model)}
                    tmp_responses['stability'] = output[isamp][0]
                    simu_path = os.path.join(path, f'simu_{isamp}')
                    save_param_study_for_simu(simu_path, 'param_study.json', tmp_design, tmp_responses)

                fig = v.Row(children=[
                        go.FigureWidget(
                            data=go.Parcoords(
                            line=dict(color = dimensions[0]['values']),
                            dimensions = dimensions,
                        )),
                        ],
                        align='center', justify='center'
                )

                def change_plot(change):
                    if only_stable.v_model:
                        mask = dimensions[0]['values'] == 1
                    else:
                        mask = slice(dimensions[0]['values'].size)

                    new_data = []
                    for i in items.v_model:
                        d = dimensions[i]
                        new_data.append(dict(values=d['values'][mask], label=d['label']))

                    fig.children = [
                            go.FigureWidget(
                                go.Parcoords(
                            line=dict(color = dimensions[color.v_model]['values'][mask]),
                            dimensions = new_data,
                        ))
                    ]

                color = v.Select(label='color', items=[{'text': v['label'], 'value': i } for i, v in enumerate(dimensions)], v_model=0)
                items = v.Select(label='Show items', items=[{'text': v['label'], 'value': i } for i, v in enumerate(dimensions)], v_model=[i for i in range(len(dimensions))], multiple=True)
                only_stable = v.Switch(label='Show only stable results', v_model=False)

                color.observe(change_plot, 'v_model')
                items.observe(change_plot, 'v_model')
                only_stable.observe(change_plot, 'v_model')

                self.plotly_plot.children = [color, items, only_stable, fig]
                self.stop_simulation(None)

            run_parametric_study()

    def stop_simulation(self, change):
        """
        Update the run button to restart the parametric study.
        """
        self.run.v_model = True
        self.run.children = ['Run parametric study']
        self.run.color = 'success'

    def purge(self, change):
        """
        Purge the design space, the plot area and the responses when
        the test case or the lb scheme are changed.
        """
        self.design.purge()
        self.plotly_plot.children = []
        self.responses.widget.v_model = []
        try:
            shutil.rmtree(self.tmp_dir.name)
        except OSError:
            # Could be some issues on Windows
            pass
