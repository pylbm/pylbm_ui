import ipyvuetify as v
import markdown
import plotly.graph_objects as go
import numpy as np
from skopt.sampler import Lhs, Sobol
import copy
import pylbm
import tempfile
import shutil
import asyncio
import pathos

from .design_space import Design_widget
from .simulation_widget import simulation
from ..utils import required_fields
from .pylbmwidget import out


def run_simulation(args):
    simu_cfg, sample, duration = args
    simu_cfg['codegen_option']['generate'] = False

    sol = pylbm.Simulation(simu_cfg, initialize=False)
    sol.extra_parameters = sample
    sol._need_init = True
    fluid_cells = sol.domain.in_or_out == sol.domain.valin
    sol.t = 0
    while sol.t <= duration:
        sol.one_time_step()
        for c in sol.scheme.consm:
            data = sol.m_halo[c][fluid_cells]
            if np.isnan(data).any() or np.any(np.abs(data)>1e10):
                return False

    return True

def run_parametric_study(args):
    from pathos.multiprocessing import ProcessingPool
    pool = ProcessingPool(nodes=4)
    return pool.map(run_simulation, args)

class parametric_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        with out:
            space_step = v.TextField(v_model=0.01, type='number')
            codegen = v.Select(items=['auto', 'numpy', 'cython'], v_model='auto')

            design = Design_widget(test_case_widget, lb_scheme_widget)

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
                    ]),
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Methods']),
                    ]),
                ], multiple=True)
            ]
            #
            # Right panel
            #
            run = v.Btn(v_model=True, children=['Run parametric study'], class_="ma-2", color='success')
            plotly_plot = v.Layout(d_flex=True)

            right_panel = [
                v.Row(children=[run]),
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

                        run.v_model = False
                        run.children = ['Stop parametric study']
                        run.color = 'error'

                        test_case = copy.deepcopy(test_case_widget.get_case())
                        lb_scheme = copy.deepcopy(lb_scheme_widget.get_case())

                        design_space = design.design_space()
                        sampling = np.asarray(Lhs().generate(list(design_space.values()), 10))

                        output = np.zeros(sampling.shape[0])

                        simu_cfg = test_case.get_dictionary()
                        param = simu_cfg['parameters']
                        simu_cfg.update(lb_scheme.get_dictionary())
                        param.update(simu_cfg['parameters'])
                        simu_cfg['parameters'] = param
                        if codegen.v_model != 'auto':
                            simu_cfg['generator'] = codegen.v_model
                        simu_cfg['codegen_option'] = {'directory': tmp_dir.name}
                        simu_cfg['space_step'] = float(space_step.v_model)

                        bound_cfg = {}
                        bound_tc = test_case.get_boundary()
                        bound_sc = lb_scheme.get_boundary()
                        for key, val in bound_tc.items():
                            bound_cfg[key] = bound_sc[val]

                        simu_cfg.pop('dim')
                        simu_cfg['boundary_conditions'] = bound_cfg

                        keys = list(simu_cfg['parameters'].keys())
                        str_keys = [str(k) for k in simu_cfg['parameters'].keys()]
                        for ik, k in enumerate(design_space.keys()):
                            if isinstance(k, tuple):
                                for kk in k:
                                    if kk in str_keys:
                                        simu_cfg['parameters'].pop(keys[str_keys.index(kk)])
                            else:
                                if k in str_keys:
                                    simu_cfg['parameters'].pop(keys[str_keys.index(k)])

                        pylbm.Simulation(simu_cfg, initialize=False)

                        args = []
                        for s in sampling:
                            design_sample = {}
                            for ik, k in enumerate(design_space.keys()):
                                if isinstance(k, tuple):
                                    for kk in k:
                                        design_sample[kk] = s[ik]
                                else:
                                    if k == 'lambda':
                                        design_sample['lambda_'] = s[ik]
                                    design_sample[k] = s[ik]
                            args.append((simu_cfg, design_sample, test_case.duration))

                        output[:] = run_parametric_study(args)

                        dimensions = [dict(values=sampling[:, ik], label=f'{k}') for ik, k in enumerate(design_space.keys())]
                        dimensions.append(dict(values=output, label='stability'))

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

                        plotly_plot.children = [fig]
                        stop_simulation(None)

                    else:
                        stop_simulation(None)

            run.on_event('click', run_study)

            def purge(change):
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