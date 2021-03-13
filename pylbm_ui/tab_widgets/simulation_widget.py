import ipywidgets as widgets
import pylbm
import asyncio
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

import ipyvuetify as v

from .save_widget import Save_widget
from .pylbmwidget import out

class simulation:
    def __init__(self):
        self.sol = None
        self.fields = None

    def init_fields(self, fields):
        self.fields = fields
        self.func = {}
        for k, v in fields.items():
            self.func[k] = sp.lambdify(list(v.atoms(sp.Symbol)), v, "numpy", dummify=False)

    def init_sol(self, test_case, lb_scheme, codegen, discret):
        simu_cfg = test_case.get_dictionary()
        param = simu_cfg['parameters']
        simu_cfg.update(lb_scheme.get_dictionary())
        param.update(simu_cfg['parameters'])
        simu_cfg['parameters'] = param
        simu_cfg['space_step'] = float(discret['dx'].v_model)
        if codegen.v_model != 'auto':
            simu_cfg['generator'] = codegen.v_model

        bound_cfg = {}
        bound_tc = test_case.get_boundary()
        bound_sc = lb_scheme.get_boundary()
        for key, val in bound_tc.items():
            bound_cfg[key] = bound_sc[val]

        simu_cfg.pop('dim')
        simu_cfg['boundary_conditions'] = bound_cfg

        self.sol = pylbm.Simulation(simu_cfg)

    def get_data(self, field):
        to_subs = {str(k): self.sol.m[k] for k in self.sol.scheme.consm.keys()}
        to_subs.update({str(k): v for k, v in self.sol.scheme.param.items()})

        args = {str(s): to_subs[str(s)] for s in self.fields[field].atoms(sp.Symbol)}
        return self.sol.t, self.sol.domain.x, self.func[field](**args)

def plot_1d(ax, scatter_plot, t, x, data):
    if scatter_plot is None:
        scatter_plot = ax.scatter(x, data, color='cadetblue', s=1)
    else:
        scatter_plot.set_offsets(np.c_[x, data])
        xmin, xmax = x[0], x[-1]
        ymin, ymax = np.amin(data), np.amax(data)
        xeps = 0.1*(xmax - xmin)
        yeps = 0.1*(ymax - ymin)
        ax.set_xlim(xmin - xeps, xmax + xeps)
        ax.set_ylim(ymin - yeps, ymax + yeps)
    plt.title(f"time: {t} s")
    return scatter_plot

def plot_2d(fig, ax, imshow_plot, t, data):
    ax.title.set_text(f"time: {t} s")

    if imshow_plot is None:
        ax.clear()
        imshow_plot = ax.imshow(data.T, origin='lower')
        cb = fig.colorbar(imshow_plot, ax=ax)
        return imshow_plot, cb
    else:
        imshow_plot.set_array(data.T)
        imshow_plot.set_clim(vmin=np.amin(data), vmax=np.amax(data))
        return imshow_plot

def prepare_simu_fig():
    plt.ioff()
    fig, ax = plt.subplots(figsize=(10,5))
    fig.canvas.header_visible = False

    return fig, ax

class simulation_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        with out:
            test_case = test_case_widget.get_case()
            lb_case = lb_scheme_widget.get_case()
            lb_param = lb_scheme_widget.parameters

            simu = simulation()
            simu.init_fields(lb_scheme_widget.get_case().equation.get_fields())

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
            left_panel = v.ExpansionPanels(children=[
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


            #
            # Right panel
            #

            start = v.Btn(v_model=True, children=['Start'], class_="ma-2", style_="width: 100px", color='success')
            pause = v.Btn(children=['Pause'], class_="ma-2", style_="width: 100px", disabled=True, v_model=False)
            progress_bar = v.ProgressLinear(height=20, value=0, color="light-blue", striped=True)
            result = v.Select(items=list(simu.fields.keys()), v_model=list(simu.fields.keys())[0])
            period = v.TextField(label='Period', v_model=16, type='number')
            self.plot = None
            self.cb = None
            fig, ax = prepare_simu_fig()
            plot_output = fig.canvas

            right_panel = [
                v.Row(children=[start, pause]),
                progress_bar,
                v.Row(children=[
                    v.Col(children=[result], sm=5),
                    v.Col(children=[period], sm=5),
                    v.Col(children=[v.Btn(children=['Snapshot'])], sm=2),
                ], align='center', justify='center'),
                v.Row(children=[plot_output])
            ]

            def stop_simulation(change):
                start.v_model = True
                start.children = ['Start']
                start.color = 'success'
                pause.disabled = True
                pause.v_model = False
                progress_bar.value = 0

            def update_result(change):
                simu.init_fields(lb_scheme_widget.get_case().equation.get_fields())
                result.items = list(simu.fields.keys())
                result.v_model = list(simu.fields.keys())[0]

            async def run_simu(simu):
                nite = 1

                test_case = test_case_widget.get_case()
                t, x, data = simu.get_data(result.v_model)

                if simu.sol.dim == 1:
                    self.plot = plot_1d(ax, None, t, x, data)
                elif simu.sol.dim == 2:
                    if self.cb:
                        self.cb.remove()
                    self.plot, self.cb = plot_2d(fig, ax, None, t, data)
                plot_output.draw_idle()

                await asyncio.sleep(0.01)
                while simu.sol.t <= test_case.duration:
                    progress_bar.value = simu.sol.t/test_case.duration*100

                    if not pause.v_model:
                        simu.sol.one_time_step()

                        if period.v_model != '' and period.v_model != 0:
                            if nite >= int(period.v_model):
                                nite = 1
                                t, x, data = simu.get_data(result.v_model)
                                if simu.sol.dim == 1:
                                    self.plot = plot_1d(ax, self.plot, t, x, data)
                                elif simu.sol.dim == 2:
                                    self.plot = plot_2d(fig, ax, self.plot, t, data)
                                plot_output.draw_idle()

                        nite += 1

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

                        test_case = test_case_widget.get_case()
                        lb_scheme = lb_scheme_widget.get_case()

                        print('init simu')

                        simu.init_sol(test_case, lb_scheme, codegen, discret)

                        print('run simu')
                        asyncio.ensure_future(run_simu(simu))
                    else:
                        stop_simulation(None)

            def on_pause_click(widget, event, data):
                pause.v_model = not pause.v_model

            def replot(change):
                t, x, data = simu.get_data(result.v_model)
                if simu.sol.dim == 1:
                    self.plot = plot_1d(ax, self.plot, t, x, data)
                elif simu.sol.dim == 2:
                    self.plot = plot_2d(fig, ax, self.plot, t, data)
                plot_output.draw_idle()

            start.on_event('click', start_simulation)
            pause.on_event('click', on_pause_click)
            result.observe(replot, 'v_model')

            test_case_widget.case.observe(stop_simulation, 'v_model')
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
                v.Col(children=[v.FileInput(), left_panel], sm=3),
                v.Col(children=right_panel)
            ])
