import ipywidgets as widgets
import pylbm
import asyncio
import os
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import json
import ipyvuetify as v

from .save_widget import Save_widget
from .pylbmwidget import out
from ..config import default_path
from ..simulation import simulation, Plot

class simulation_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        with out:
            test_case = test_case_widget.get_case()
            lb_case = lb_scheme_widget.get_case()
            lb_param = lb_scheme_widget.parameters

            simu = simulation()
            simu.reset_fields(lb_scheme_widget.get_case().equation.get_fields())

            simulation_name = v.TextField(label='Simulation name', v_model='simu_0')
            nx = 201
            dx = test_case.size()/201
            dt = dx*float(lb_param['la'].v_model)
            nt = test_case.duration/dt
            discret = {
                'nx': v.TextField(label='Number of points', v_model=nx, value=nx, type='number'),
                'dx': v.TextField(label='Space step', v_model=dx, value=dx, type='number'),
                'nt': v.TextField(label='Number of steps', v_model=nt, value=nt, type='number'),
                'dt': v.TextField(label='Time step', v_model=dt, value=dt, type='number'),
            }

            codegen = v.Select(items=['auto', 'numpy', 'cython'], v_model='auto')
            left_panel = [
                simulation_name,
                v.ExpansionPanels(children=[
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Discretization']),
                        v.ExpansionPanelContent(children=[
                            v.Card(children=[
                                v.CardTitle(children=['In space']),
                                v.CardText(children=[
                                    discret['nx'],
                                    discret['dx'],
                                ]),
                            ], class_="ma-2"),
                            v.Card(children=[
                                v.CardTitle(children=['In time']),
                                v.CardText(children=[
                                    discret['nt'],
                                    discret['dt'],
                                ]),
                            ], class_="ma-2"),
                            v.Card(children=[
                                v.CardTitle(children=['Scheme velocity']),
                                v.CardText(children=[
                                    lb_param['la']
                                ]),
                            ], class_="ma-2"),
                        ]),
                    ]),
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Code generator']),
                        v.ExpansionPanelContent(children=[codegen]),
                    ]),
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Field output request']),
                        v.ExpansionPanelContent(children=[
                            Save_widget(list(lb_scheme_widget.get_case().equation.get_fields().keys())).widget
                        ]),
                    ]),
                ], multiple=True)
            ]

            #
            # Right panel
            #

            start = v.Btn(v_model=True, children=['Start'], class_="ma-2", style_="width: 100px", color='success')
            pause = v.Btn(children=['Pause'], class_="ma-2", style_="width: 100px", disabled=True, v_model=False)
            progress_bar = v.ProgressLinear(height=20, value=0, color="light-blue", striped=True)
            result = v.Select(items=list(simu.fields.keys()), v_model=list(simu.fields.keys())[0])
            period = v.TextField(label='Period', v_model=16, type='number')
            snapshot = v.Btn(children=['Snapshot'])
            self.plot = Plot()
            self.iplot = 0
            plot_output = v.Row(align='center', justify='center')

            right_panel = [
                v.Row(children=[start, pause]),
                progress_bar,
                v.Row(children=[
                    v.Col(children=[result], sm=5),
                    v.Col(children=[period], sm=5),
                    v.Col(children=[snapshot], sm=2),
                ], align='center', justify='center'),
                plot_output
            ]

            def stop_simulation(change):
                start.v_model = True
                start.children = ['Start']
                start.color = 'success'
                pause.disabled = True
                pause.v_model = False

            def update_result(change):
                simu.reset_fields(lb_scheme_widget.get_case().equation.get_fields())
                result.items = list(simu.fields.keys())
                result.v_model = list(simu.fields.keys())[0]

            async def run_simu(simu):
            # def run_simu(simu):
            #     with out:
                    nite = 1

                    simu.plot(self.plot, result.v_model)
                    plot_output.children[0].draw_idle()

                    await asyncio.sleep(0.01)
                    while simu.sol.t <= simu.duration:
                        progress_bar.value = float(simu.sol.t)/simu.duration*100

                        if not pause.v_model:
                            simu.sol.one_time_step()

                            if period.v_model != '' and period.v_model != 0:
                                if nite >= int(period.v_model):
                                    nite = 1
                                    simu.save_data(result.v_model)
                                    simu.plot(self.plot, result.v_model)
                                    plot_output.children[0].draw_idle()

                            nite += 1
                            self.iplot += 1

                        await asyncio.sleep(0.01)
                        if start.v_model:
                            break
                    stop_simulation(None)

            def start_simulation(widget, event, data):
                with out:
                    if start.v_model:
                        start.v_model = False
                        start.children = ['Stop']
                        start.color = 'error'
                        pause.disabled = False
                        progress_bar.value = 0

                        self.plot = Plot()
                        self.iplot = 0
                        plot_output.children = [self.plot.fig.canvas]

                        test_case = test_case_widget.get_case()
                        lb_scheme = lb_scheme_widget.get_case()

                        simu.reset_path(os.path.join(default_path, simulation_name.v_model))
                        simu.reset_sol(test_case, lb_scheme, float(discret['dx'].v_model), codegen.v_model)
                        simu.save_config()

                        asyncio.ensure_future(run_simu(simu))
                        # run_simu(simu)
                    else:
                        stop_simulation(None)

            def on_pause_click(widget, event, data):
                pause.v_model = not pause.v_model

            def replot(change):
                if self.plot:
                    simu.plot(self.plot, result.v_model)
                    plot_output.children[0].draw_idle()

            def take_snapshot(widget, event, data):
                if self.plot:
                    self.plot.fig.savefig(os.path.join(simu.path, f'snapshot_{result.v_model}_{self.iplot}.png'), dpi=300)

            start.on_event('click', start_simulation)
            pause.on_event('click', on_pause_click)
            snapshot.on_event('click', take_snapshot)
            result.observe(replot, 'v_model')

            test_case_widget.select_case.observe(stop_simulation, 'v_model')
            lb_scheme_widget.select_case.observe(stop_simulation, 'v_model')
            lb_scheme_widget.select_case.observe(update_result, 'v_model')

            def observer(change):
                with out:
                    key = None
                    for k, value in discret.items():
                        if value == change.owner:
                            key = k
                            break


                    problem_size = test_case_widget.get_case().size()
                    la = float(lb_param['la'].v_model)

                    if key == 'nx' or key is None:
                        nx = float(discret['nx'].v_model)
                        dx = problem_size/nx
                        discret['dx'].v_model = dx
                        discret['nt'].v_model = la*nx
                        discret['dt'].v_model = dx/la
                    elif key == 'dx':
                        dx = float(discret['dx'].v_model)
                        discret['nx'].v_model = problem_size/dx
                        discret['nt'].v_model = la*discret['nx'].v_model
                        discret['dt'].v_model = dx/la
                    elif key == 'nt':
                        nt = float(discret['nt'].v_model)
                        discret['nx'].v_model = nt/la
                        discret['dx'].v_model = problem_size/discret['nx'].v_model
                        discret['dt'].v_model = discret['dx'].v_model/la
                    elif key == 'dt':
                        dt = float(discret['dt'].v_model)
                        discret['dx'].v_model = dt*la
                        discret['nx'].v_model = problem_size/discret['dx'].v_model
                        discret['nt'].v_model = la*discret['nx'].v_model

            for value in discret.values():
                value.observe(observer, 'v_model')
            lb_param['la'].observe(observer, 'v_model')

            self.widget = v.Row(children=[
                v.Col(children=left_panel, sm=3),
                v.Col(children=right_panel)
            ])
