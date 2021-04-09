import ipyvuetify as v
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
from ..responses import From_config, From_simulation
from ..simulation import simulation, get_config
from ..utils import required_fields
from .pylbmwidget import out


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
            space_step = v.TextField(label='Space step', v_model=0.01, type='number')
            codegen = v.Select(label='Code generator', items=['auto', 'numpy', 'cython'], v_model='auto')

            design = Design_widget(test_case_widget, lb_scheme_widget)
            responses = Responses_widget(test_case_widget, lb_scheme_widget)
            run = v.Btn(v_model=True, children=['Run parametric study'], class_="ma-5", color='success')
            plotly_plot = v.Container(align_content_center=True)

            sampling_method = v.Select(label='Method', items=list(skopt_method.keys()), v_model=list(skopt_method.keys())[0])
            sample_size = v.TextField(label='Number of samples', v_model=10, type='number')

            left_panel = [
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

                        design_space = design.design_space()
                        if design_space:
                            run.v_model = False
                            run.children = ['Stop parametric study']
                            run.color = 'error'

                            test_case = copy.deepcopy(test_case_widget.get_case())
                            lb_scheme = copy.deepcopy(lb_scheme_widget.get_case())

                            alert = v.Alert(children=['Initialize...'], class_='primary--text')
                            plotly_plot.children = [
                                v.Row(children=[
                                    v.ProgressCircular(indeterminate=True, color='primary', size=70, width=4)
                                    ], align='center', justify='center'),
                                v.Row(children=[
                                    alert
                                    ], align='center', justify='center')
                            ]
                            sampling = np.asarray(skopt_method[sampling_method.v_model]().generate(list(design_space.values()), int(sample_size.v_model)))

                            alert.children = ['Prepare the simulation...']
                            simu = simulation()
                            simu.reset_sol(test_case, lb_scheme, float(space_step.v_model), codegen.v_model, exclude=design_space.keys(), initialize=False, codegen_dir=tmp_dir.name, show_code=False)

                            args = []
                            tmp_case = test_case.copy()
                            for s in sampling:
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

                                simu_cfg = get_config(tmp_case, lb_scheme, float(space_step.v_model), codegen.v_model, exclude=design_space.keys(), codegen_dir=tmp_dir.name)

                                args.append((simu_cfg, design_sample, tmp_case.duration, responses.get_list(tmp_case, simu_cfg)))

                            alert.children = ['Run simulations on the sampling...']

                            # async def run_parametric_study():
                            def run_parametric_study():
                                with out:
                                    from pathos.multiprocessing import ProcessingPool
                                    pool = pp.ProcessPool()
                                    output = pool.map(run_simulation, args)

                                    # output = []
                                    # for a in args:
                                    #     output.append(run_simulation(a))

                                    dimensions = [dict(values=sampling[:, ik], label=f'{k}') for ik, k in enumerate(design_space.keys())]

                                    dimensions.append(dict(values=np.asarray([o[0] for o in output], dtype=np.float64), label='stability'))

                                    for i, r in enumerate(responses.widget.v_model):
                                        dimensions.append(dict(values=np.asarray([o[i+1] for o in output], dtype=np.float64), label=r))

                                    fig = go.FigureWidget(
                                            data=go.Parcoords(
                                            line=dict(color = output),
                                            dimensions = dimensions,
                                        ),
                                    )

                                    fig.update_layout(
                                        autosize=False,
                                        width=800,
                                        height=600,)

                                    print(dimensions)
                                    plotly_plot.children = [v.Row(children=[fig], align='center', justify='center')]
                                    stop_simulation(None)
                            # asyncio.ensure_future(run_parametric_study())
                            run_parametric_study()

                            # output[:] = run_parametric_study(args)

                            # dimensions = [dict(values=sampling[:, ik], label=f'{k}') for ik, k in enumerate(design_space.keys())]
                            # dimensions.append(dict(values=output, label='stability'))

                            # fig = go.FigureWidget(
                            #     data=go.Parcoords(
                            #         line=dict(color = output),
                            #         dimensions = dimensions,
                            #     ),
                            # )

                            # fig.update_layout(
                            #     autosize=False,
                            #     width=800,
                            #     height=600,)

                            # plotly_plot.children = [fig]
                        # stop_simulation(None)

                    else:
                        stop_simulation(None)

            run.on_event('click', run_study)

            def purge(change):
                design.purge()
                plotly_plot.children = []
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