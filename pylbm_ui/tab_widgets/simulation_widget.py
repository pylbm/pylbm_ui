from ipywidgets import HBox, VBox, GridspecLayout, Dropdown, Layout, Button, FloatProgress, Text, HTML, Accordion, SelectMultiple, Tab, Output, ToggleButton, IntText, FloatText
import ipywidgets as widgets
import pylbm
import asyncio
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from ipympl.backend_nbagg import Canvas


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
        simu_cfg = test_case.value.get_dictionary()
        param = simu_cfg['parameters']
        simu_cfg.update(lb_scheme.value.get_dictionary())
        param.update(simu_cfg['parameters'])
        simu_cfg['parameters'] = param
        simu_cfg['space_step'] = discret['dx'].value
        if codegen.value != 'auto':
            simu_cfg['generator'] = codegen.value

        bound_cfg = {}
        bound_tc = test_case.value.get_boundary()
        bound_sc = lb_scheme.value.get_boundary()
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

def plot(ax, scatter_plot, t, x, data):
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

def prepare_simu_fig():
    plt.ioff()
    fig, ax = plt.subplots(figsize=(10,5))
    fig.canvas.header_visible = False

    return fig.canvas

class simulation_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):

        default_layout = Layout(width='90%')

        test_case = test_case_widget.case
        lb_scheme = lb_scheme_widget.case
        case_parameters = lb_scheme_widget.case_parameters

        pause = ToggleButton(value=False,
                            description='Pause',
                            disabled=True,
        )
        start = ToggleButton(value=False,
                       description='Start',
                       button_style='success',
        )
        progress = FloatProgress(value=0.0, min=0.0, max=1.0,
                                 layout=Layout(width='80%')
        )

        codegen = Dropdown(options=['auto', 'numpy', 'cython'],
                           layout=default_layout,
        )

        simu = simulation()
        simu.init_fields(lb_scheme.value.equation.get_fields())
        fields_select = SelectMultiple(options=simu.fields.keys(),
                                # description='<b>field(s)</b>',
                                # style={'description_width': '50px'},
                                layout=default_layout,
        )

        results = Dropdown(options=simu.fields.keys(),
                           layout=Layout(width="35%")
        )
        period = IntText(value=16,
                         description='period (step):',
                         continuous_update=True,
                         layout=Layout(width="35%")
        )
        snapshot = Button(description='snapshot',
                          button_style='primary',
                          layout=Layout(width="20%")
        )

        self.scatter_plot = None
        plot_output = prepare_simu_fig()

        discret = {'nx': IntText(value=101,
                                 continuous_update=True,
                                 description='$N_{points}$',
                                 style={'description_width': '50px'},
                                 layout=default_layout),
                   'dx': FloatText(value=test_case.value.size()/100,
                                   continuous_update=True,
                                   description='$\Delta x$',
                                   style={'description_width': '50px'},
                                   layout=default_layout),
                   'nt': IntText(value=case_parameters['la'].value*101,
                                 continuous_update=True,
                                 description='$N_{step}$',
                                 style={'description_width': '50px'},
                                 layout=default_layout),
                   'dt': FloatText(value=case_parameters['la'].value/100,
                                   continuous_update=True,
                                   description='$\Delta t$',
                                   style={'description_width': '50px'},
                                   layout=default_layout),
        }


        artificial = Dropdown(options=['OFF', 'Mass', 'Momentum', 'Energy', 'Pressure'],
                             tooltip="select the detector for artificial viscosity. Select OFF to avoid the use of artificial viscosity", layout=default_layout)
        thetaFunc = Dropdown(options=["power","tanh"], layout=default_layout)
        chi = FloatText(value = 2, description='Chi', tooltip="theta_chi", continuous_update=False, layout=default_layout)
        threshold = FloatText(value = 1, description='Threshold', tooltip="theta_threshold", continuous_update=False, layout=default_layout)
        sharpness = FloatText(value = 1, description='Sharpness', tooltip="theta_sharpness", continuous_update=False, layout=default_layout)

        left_panel = VBox([HTML(value='<u><b>Simulation name</u></b>'),
                           Text(value='simu',
                                layout=default_layout
                            ),
                           HTML(value='<u><b>Settings</u></b>'),
                           Accordion(children=[VBox([HTML('<b>In space</b>'), discret['nx'], discret['dx'],
                                                     HTML('<b>In time</b>'), discret['nt'], discret['dt'],
                                                     case_parameters['la'],
                                     ])],
                                     _titles={0: 'Discretization'},
                                     selected_index=None,
                                     layout=default_layout),
                           Accordion(children=[codegen],
                                     _titles={0: 'Code generator'},
                                     selected_index=None,
                                     layout=default_layout),
                           Accordion(children=[fields_select],
                                     _titles={0: 'Field output request'},
                                     selected_index=None,
                                     layout=default_layout),
                           Accordion(children=[VBox([artificial,
                                                    Accordion(children=[VBox([thetaFunc,
                                                                              chi,
                                                                              threshold,
                                                                              sharpness])],
                                                              _titles={0: 'Parameters'},
                                                              selected_index=None,
                                                              layout=default_layout)])],
                                     _titles={0: 'Artificial viscosity'},
                                     selected_index=None,
                                     layout=default_layout),
                            ],
                           layout=Layout(align_items='center', margin= '10px')
        )

        right_panel = Tab([VBox([HBox([results, period, snapshot],
                                 layout=Layout(display='flex', justify_content='space-between')),
                                 plot_output])],
                          _titles= {0: 'Live results',
                          },
        )

        async def run_simu(simu):
            nite = 1

            t, x, data = simu.get_data(results.value)
            self.scatter_plot = plot(ax, self.scatter_plot, t, x, data)
            plot_output.draw_idle()

            await asyncio.sleep(0.01)
            while simu.sol.t <= test_case.value.duration:
                progress.value = simu.sol.t/test_case.value.duration

                if not pause.value:
                    simu.sol.one_time_step()

                    if nite >= period.value:
                        nite = 1
                        t, x, data = simu.get_data(results.value)
                        self.scatter_plot = plot(ax, self.scatter_plot, t, x, data)
                        plot_output.draw_idle()

                    nite += 1

                await asyncio.sleep(0.1)
                if not start.value:
                    break
            start.value = False

        def start_simulation(change):
            if start.value:
                start.description = 'Stop'
                start.button_style = 'danger'
                pause.disabled = False
                simu.init_sol(test_case, lb_scheme, codegen, discret)

                asyncio.ensure_future(run_simu(simu))
            else:
                start.description = 'Start'
                start.button_style = 'success'
                pause.disabled = False
                pause.value = False

        start.observe(start_simulation, 'value')

        # FIX: We should only keep dx
        def observer(change):
            key = None
            for k, v in discret.items():
                if v == change.owner:
                    key = k
                    break

            if key == 'nx' or key is None:
                discret['dx'].value = test_case.value.size()/discret['nx'].value
                discret['nt'].value = case_parameters['la'].value*discret['nx'].value
                discret['dt'].value = discret['dx'].value/case_parameters['la'].value
            elif key == 'dx':
                discret['nx'].value = test_case.value.size()/discret['dx'].value
                discret['nt'].value = case_parameters['la'].value*discret['nx'].value
                discret['dt'].value = discret['dx'].value/case_parameters['la'].value
            elif key == 'nt':
                discret['nx'].value = discret['nt'].value/case_parameters['la'].value
                discret['dx'].value = test_case.value.size()/discret['nx'].value
                discret['dt'].value = discret['dx'].value/case_parameters['la'].value
            elif key == 'dt':
                discret['dx'].value = discret['dt'].value*case_parameters['la'].value
                discret['nx'].value = test_case.value.size()/discret['dx'].value
                discret['nt'].value = case_parameters['la'].value*discret['nx'].value

        for v in discret.values():
            v.observe(observer, 'value')
        case_parameters['la'].observe(observer, 'value')

        self.widget = VBox([HBox([start, pause, progress]),
                            GridspecLayout(1, 4)])
        self.widget.children[1][0, 0] = left_panel
        self.widget.children[1][0, 1:] = right_panel

