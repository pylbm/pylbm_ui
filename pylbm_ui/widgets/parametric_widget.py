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

from .design_space import Design_widget
from .responses import Responses_widget
from ..config import default_path
from ..responses import From_config, From_simulation
from ..simulation import simulation, get_config
from ..utils import required_fields
from ..json import save_simu_config, save_param_study_for_simu
from .pylbmwidget import out
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
        if isinstance(r, From_config):
            output[i] = r(simu_cfg, sample)

    nan_detected = False
    nite = 0
    while sol.t <= duration and not nan_detected:
        sol.one_time_step()

        if nite == 200:
            nite = 0
            c = list(sol.scheme.consm.keys())[0]
            sol.m_halo[c][solid_cells] = 0
            data = sol.m[c]
            if np.isnan(np.sum(data)):
                nan_detected = True
        nite += 1


    for i, r in enumerate(responses):
        if isinstance(r, From_simulation):
            output[i] = r(sol)

    return [not nan_detected] + output

skopt_method = {'Latin hypercube': Lhs,
                'Sobol': Sobol,
                'Halton': Halton,
                'Hammersly': Hammersly,
}
class parametric_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        with out:
            study_name = v.TextField(label='Study name', v_model='PS_0')

            space_step = v.TextField(label='Space step', v_model=0.01, type='number')
            codegen = v.Select(label='Code generator', items=['auto', 'numpy', 'cython'], v_model='auto')

            design = Design_widget(test_case_widget, lb_scheme_widget)
            responses = Responses_widget(test_case_widget, lb_scheme_widget)
            run = v.Btn(v_model=True, children=['Run parametric study'], class_="ma-5", color='success')
            plotly_plot = v.Container(align_content_center=True)

            sampling_method = v.Select(label='Method', items=list(skopt_method.keys()), v_model=list(skopt_method.keys())[0])
            sample_size = v.TextField(label='Number of samples', v_model=10, type='number')

            left_panel = [
                study_name,
                space_step,
                codegen,
                v.ExpansionPanels(children=[
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Design space']),
                        v.ExpansionPanelContent(children=[design.widget]),
                    ]),
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Responses']),
                        v.ExpansionPanelContent(children=[responses.widget]),
                    ]),
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Sampling method']),
                        v.ExpansionPanelContent(children=[sampling_method, sample_size]),
                    ]),
                ], multiple=True),
                v.Row(children=[run], align='center', justify='center'),
            ]
            #
            # Right panel
            #
            right_panel = [
                v.Row(children=[plotly_plot])
            ]

            tmp_dir = tempfile.TemporaryDirectory()
            def stop_simulation(change):
                run.v_model = True
                run.children = ['Run parametric study']
                run.color = 'success'

            def run_study(widget, event, data):
                with out:
                    if run.v_model:
                        print(tmp_dir.name)

                        try:
                            shutil.rmtree(tmp_dir.name)
                        except OSError:
                            # Could be some issues on Windows
                            pass

                        path = os.path.join(default_path, study_name.v_model)

                        design_space = design.design_space()
                        if design_space:
                            run.v_model = False
                            run.children = ['Stop parametric study']
                            run.color = 'error'

                            test_case = copy.deepcopy(test_case_widget.get_case())
                            lb_scheme = copy.deepcopy(lb_scheme_widget.get_case())

                            message = Message('Initialize')
                            plotly_plot.children = [message]
                            sampling = np.asarray(skopt_method[sampling_method.v_model]().generate(list(design_space.values()), int(sample_size.v_model)))

                            message.update('Prepare the simulation')
                            simu = simulation()
                            simu.reset_sol(test_case, lb_scheme, float(space_step.v_model), codegen.v_model, exclude=design_space.keys(), initialize=False, codegen_dir=tmp_dir.name, show_code=False)

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


                                la = lb_scheme.la.value
                                if lb_scheme.la.symb in design_sample:
                                    la = design_sample[lb_scheme.la.symb]
                                dx = float(space_step.v_model)
                                dt = dx/la

                                duration = test_case.duration
                                if 'duration' in design_sample:
                                    duration = design_sample['duration']

                                tmp_case.duration = np.floor(test_case.duration/dt)*dt
                                if tmp_case.duration%dt != 0:
                                    tmp_case.duration += dt

                                simu_path = os.path.join(path, f'simu_{i}')
                                simu_cfg = get_config(tmp_case, lb_scheme, float(space_step.v_model), codegen.v_model, exclude=design_space.keys(), codegen_dir=tmp_dir.name)
                                save_simu_config(simu_path, 'simu_cfg.json', float(space_step.v_model), tmp_case, lb_scheme, {str(k): v for k, v in design_sample.items()})
                                args.append((simu_cfg, design_sample, tmp_case.duration, responses.get_list(simu_path, tmp_case, simu_cfg)))

                            message.update('Run simulations on the sampling...')

                            # async def run_parametric_study():
                            def run_parametric_study():
                                with out:
                                    from pathos.multiprocessing import ProcessingPool
                                    pool = pp.ProcessPool()
                                    output = pool.map(run_simulation, args)

                                    dimensions = [dict(values=np.asarray([o[0] for o in output], dtype=np.float64), label='stability')]

                                    dimensions.extend([dict(values=sampling[:, ik], label=f'{k}') for ik, k in enumerate(design_space.keys())])

                                    for i, r in enumerate(responses.widget.v_model):
                                        if output[0][i+1] is not None:
                                            dimensions.append(dict(values=np.asarray([o[i+1] for o in output], dtype=np.float64), label=r))

                                    for isamp in range(len(sampling)):
                                        tmp_design = {f'{k}': sampling[isamp, ik] for ik, k in enumerate(design_space.keys())}
                                        tmp_responses = {r: output[isamp][ir + 1] for ir, r in enumerate(responses.widget.v_model)}
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
                                        with out:
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

                                    plotly_plot.children = [color, items, only_stable, fig]
                                    stop_simulation(None)
                            # asyncio.ensure_future(run_parametric_study())
                            run_parametric_study()
                    else:
                        stop_simulation(None)

            run.on_event('click', run_study)

            def purge(change):
                design.purge()
                plotly_plot.children = []
                responses.widget.v_model = []
                try:
                    shutil.rmtree(tmp_dir.name)
                except OSError:
                    # Could be some issues on Windows
                    pass

            test_case_widget.select_case.observe(purge, 'v_model')
            lb_scheme_widget.select_case.observe(purge, 'v_model')
            codegen.observe(purge, 'v_model')

            self.widget = v.Row(children=[
                v.Col(children=left_panel, sm=3),
                v.Col(children=right_panel)
            ])

            self.main = right_panel
            self.menu = left_panel