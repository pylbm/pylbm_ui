# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

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
from .pylbmwidget import Tooltip, out, debug_widget
from .dialog_path import DialogPath
from ..config import default_path, nb_split_period, default_dx
from ..simulation import simulation, Plot
from ..utils import StrictlyPositiveIntField, StrictlyPositiveFloatField, NbPointsField
from .message import Message

class simulation_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        with out:
            test_case = test_case_widget.get_case()
            tc_param = test_case_widget.parameters
            lb_case = lb_scheme_widget.get_case()
            lb_param = lb_scheme_widget.parameters

            simu = simulation()
            simu.reset_fields(lb_scheme_widget.get_case().equation.get_fields())

            simulation_name = v.TextField(label='Simulation name', v_model='simu_0')
            input_file = v.FileInput(label='Choose a simu_config.json', accept=".json")
            dx = default_dx
            nx = int(test_case.size()[0]/dx) + 1
            ny = 1
            dt = dx/lb_param['la'].value
            nt = int(test_case.duration/dt)
            la_vue = v.CardText(children=[lb_param['la']])
            discret = {
                'nx': NbPointsField(label='Number of points in x', v_model=nx, disabled=True),
                'ny': NbPointsField(label='Number of points in y', v_model=ny, disabled=True, class_='d-none'),
                'dx': StrictlyPositiveFloatField(label='Space step', v_model=dx),
                'nt': StrictlyPositiveIntField(label='Number of steps', v_model=nt, disable=True),
                'dt': StrictlyPositiveFloatField(label='Time step', v_model=dt),
            }

            codegen = v.Select(items=['auto', 'numpy', 'cython'], v_model='auto')
            save_fields = Save_widget(list(lb_scheme_widget.get_case().equation.get_fields().keys()))
            left_panel = [
                simulation_name,
                input_file,
                v.ExpansionPanels(children=[
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Discretization']),
                        v.ExpansionPanelContent(children=[
                            v.Card(children=[
                                v.CardTitle(children=['In space']),
                                v.CardText(children=[
                                    discret['nx'],
                                    discret['ny'],
                                    discret['dx'],
                                ]),
                            ], class_="ma-1"),
                            v.Card(children=[
                                v.CardTitle(children=['In time']),
                                v.CardText(children=[
                                    discret['nt'],
                                    discret['dt'],
                                ]),
                            ], class_="ma-1"),
                            v.Card(children=[
                                v.CardTitle(children=['Scheme velocity']),
                                la_vue,
                            ], class_="ma-1"),
                        ], class_="px-1"),
                    ]),
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Code generator']),
                        v.ExpansionPanelContent(children=[codegen]),
                    ]),
                    v.ExpansionPanel(children=[
                        v.ExpansionPanelHeader(children=['Field output request']),
                        v.ExpansionPanelContent(children=[
                            save_fields.widget
                        ]),
                    ]),
                ], multiple=True, class_='pa-0')
            ]

            #
            # Right panel
            #

            start = v.Btn(v_model=True, children=['Start'], class_='ma-2', style_='width: 100px', color='success')
            startTooltip = Tooltip(start, tooltip='click to start the simulation')

            pause = v.Btn(children=['Pause'], class_='ma-2', style_='width: 100px', disabled=True, v_model=False)
            progress_bar = v.ProgressLinear(height=20, value=0, color='light-blue', striped=True)
            result = v.Select(items=list(simu.fields.keys()), v_model=list(simu.fields.keys())[0])
            period = StrictlyPositiveIntField(label='Period', v_model=nt/nb_split_period)
            snapshot = v.Btn(children=['Snapshot'])
            self.plot = Plot()
            self.iplot = 0
            plot_output = v.Row(justify='center')

            dialog = DialogPath()

            right_panel = [
                v.Row(children=[
                    startTooltip,
                    Tooltip(pause, tooltip='click to pause the simulation'),
                    dialog,
                ]),
                progress_bar,
                v.Row(children=[
                    v.Col(children=[result], md=5, sm=12),
                    v.Col(children=[period], md=5, sm=12),
                    v.Col(children=[snapshot], md=2, sm=12),
                ], align='center', justify='space-around', ),
                plot_output,
            ]

            def stop_simulation(change):
                start.v_model = True
                start.children = ['Start']
                startTooltip.children = ['click to start the simulation']
                start.color = 'success'
                pause.disabled = True
                pause.v_model = False

            def update_result(change):
                simu.reset_fields(lb_scheme_widget.get_case().equation.get_fields())
                result.items = list(simu.fields.keys())
                result.v_model = list(simu.fields.keys())[0]

            async def run_simu():
            # def run_simu(simu):
                while dialog.v_model:
                    await asyncio.sleep(0.01)

                if not dialog.replace:
                    stop_simulation(None)
                    return

                nite = 1

                plot_output.children = [Message('Prepare the simulation')]

                test_case = test_case_widget.get_case()
                lb_scheme = lb_scheme_widget.get_case()

                simu.reset_path(os.path.join(default_path, simulation_name.v_model))
                simu.reset_sol(test_case, lb_scheme, discret['dx'].value, codegen.v_model)
                simu.save_config()

                self.plot = Plot()
                self.iplot = 0
                plot_output.children = [self.plot.fig.canvas]

                simu.plot(self.plot, result.v_model)
                plot_output.children[0].draw_idle()

                ite_to_save = save_fields.get_save_time(simu.sol.dt, simu.duration)

                await asyncio.sleep(0.01)
                while simu.sol.t <= simu.duration:
                    progress_bar.value = float(simu.sol.t)/simu.duration*100

                    if not pause.v_model:
                        simu.sol.one_time_step()

                        if not period.error:
                            if nite >= period.value:
                                nite = 1
                                simu.save_data(result.v_model)
                                simu.plot(self.plot, result.v_model)
                                plot_output.children[0].draw_idle()
                                # await asyncio.sleep(0.2)

                        if simu.sol.nt in ite_to_save:
                            simu.save_data(ite_to_save[simu.sol.nt])

                        nite += 1
                        self.iplot += 1

                    await asyncio.sleep(0.001)
                    if start.v_model:
                        break
                stop_simulation(None)

            def start_simulation(widget, event, data):
                with out:
                    if start.v_model:
                        simu_path = os.path.join(default_path, simulation_name.v_model)
                        dialog.check_path(simu_path)

                        start.v_model = False
                        start.children = ['Stop']
                        start.color = 'error'

                        pause.disabled = False
                        progress_bar.value = 0

                        asyncio.ensure_future(run_simu())
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
                    self.plot.fig.savefig(os.path.join(simu.path, f'snapshot_{result.v_model}_{self.iplot}.png'), dpi=300,  bbox_inches='tight')

            start.on_event('click', start_simulation)
            pause.on_event('click', on_pause_click)
            snapshot.on_event('click', take_snapshot)
            result.observe(replot, 'v_model')

            test_case_widget.select_case.observe(stop_simulation, 'v_model')
            lb_scheme_widget.select_case.observe(stop_simulation, 'v_model')
            lb_scheme_widget.select_case.observe(update_result, 'v_model')

            def observer(change):
                with out:
                    tc_param = test_case_widget.parameters
                    lb_param = lb_scheme_widget.parameters
                    error = lb_param['la'].error
                    for v in discret.values():
                        error |= v.error

                    if not error:
                        key = None

                        if hasattr(change, 'owner'):
                            for k, value in discret.items():
                                if value == change.owner:
                                    key = k
                                    break

                        for value in discret.values():
                            value.unobserve(observer, 'v_model')
                        lb_param['la'].unobserve(observer, 'v_model')

                        test_case = test_case_widget.get_case()
                        problem_size = [tc_param['xmax'].value - tc_param['xmin'].value]
                        if 'ymin' in tc_param:
                            problem_size.append(tc_param['ymax'].value - tc_param['ymin'].value)

                        duration = test_case.duration
                        la = lb_param['la'].value

                        if key is None or key == 'dx':
                            dx = discret['dx'].value
                            size = problem_size
                            nmin = round(min(size)/dx + 1)
                            dx = min(size)/(nmin - 1)
                            n = [round(s/dx) + 1 for s in size]
                            L = [(i-1)*dx for i in n]

                            discret['dx'].value = dx
                            discret['nx'].value = n[0]
                            if len(n) > 1:
                                discret['ny'].value = n[1]

                            test_case.set_size(L)
                            discret['dt'].value = discret['dx'].value/la
                            discret['nt'].value = duration/discret['dt'].value
                        elif key == 'nt':
                            discret['dt'].value = duration/discret['nt'].value
                            lb_param['la'].value = discret['dx'].value/discret['dt'].value
                        elif key == 'dt':
                            dt = discret['dt'].value
                            lb_param['la'].value = discret['dx'].value/discret['dt'].value
                            discret['nt'].value = duration/discret['dt'].value

                        period.value = discret['nt'].value/nb_split_period

                        for value in discret.values():
                            value.observe(observer, 'v_model')
                        lb_param['la'].observe(observer, 'v_model')


            for value in discret.values():
                value.observe(observer, 'v_model')
            lb_param['la'].observe(observer, 'v_model')
            tc_param['xmin'].observe(observer, 'v_model')
            tc_param['xmax'].observe(observer, 'v_model')
            if test_case_widget.get_case().dim > 1:
                tc_param['ymin'].observe(observer, 'v_model')
                tc_param['ymax'].observe(observer, 'v_model')

            def change_dim(change):
                with out:
                    dim = test_case_widget.get_case().dim
                    if dim == 1:
                        discret['ny'].class_ = 'd-none'
                    else:
                        discret['ny'].class_ = ''

                    tc_param = test_case_widget.parameters
                    lb_param = lb_scheme_widget.parameters
                    la_vue.children = [lb_param['la']]
                    lb_param['la'].observe(observer, 'v_model')
                    tc_param['xmin'].observe(observer, 'v_model')
                    tc_param['xmax'].observe(observer, 'v_model')
                    if test_case_widget.get_case().dim > 1:
                        tc_param['ymin'].observe(observer, 'v_model')
                        tc_param['ymax'].observe(observer, 'v_model')
                    observer(None)
            test_case_widget.select_case.observe(change_dim, 'v_model')

            self.widget = v.Row(children=[
                v.Col(children=left_panel, sm=3),
                v.Col(children=right_panel)
            ])

            self.main = right_panel
            self.menu = left_panel