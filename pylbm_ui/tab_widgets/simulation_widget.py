from ipywidgets import HBox, VBox, GridspecLayout, Dropdown, Layout, Button, FloatProgress, Text, HTML, Accordion, SelectMultiple, Tab, Output, ToggleButton, IntText, FloatText
import ipywidgets as widgets
import pylbm
import asyncio
import sympy as sp

def plot(x, data):
    viewer = pylbm.viewer.matplotlib_viewer
    fig = viewer.Fig(1, 1, figsize=(12, 8))
    col = 'navy'
    symb = '^'
    fig[0, 0].CurveScatter(x, data, color=col, alpha=0.5, symbol=symb)

    fig.show()

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

        fields = lb_scheme.value.equation.get_fields()
        fields_select = SelectMultiple(options=fields.keys(),
                                # description='<b>field(s)</b>',
                                # style={'description_width': '50px'},
                                layout=default_layout,
        )

        results = Dropdown(options=fields.keys(),
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

        plot_output = Output()


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
                            ],
                           layout=Layout(align_items='center', margin= '10px')
        )

        right_panel = Tab([VBox([HBox([results, period, snapshot],
                                 layout=Layout(display='flex', justify_content='space-between')),
                                 plot_output])],
                          _titles= {0: 'Live results',
                          },
                          layout={'height': '550px'}
        )

        func = {}
        for k, v in fields.items():
            func[k] = sp.lambdify(v.atoms(sp.Symbol), v, "numpy", dummify=False)

        async def run_simu(sol):
            nite = 1
            to_subs = {str(k): sol.m[k] for k in sol.scheme.consm.keys()}
            to_subs.update({str(k): v for k, v in sol.scheme.param.items()})
            await asyncio.sleep(0.01)
            while sol.t < test_case.value.duration:
                progress.value = sol.t/test_case.value.duration

                if not pause.value:
                    sol.one_time_step()

                    if nite >= period.value:
                        nite = 1
                        with plot_output:
                            args = {str(s): to_subs[str(s)] for s in fields[results.value].atoms(sp.Symbol)}
                            data = func[results.value](**args)
                            plot_output.clear_output(wait=True)
                            plot(sol.domain.x, data)
                            widgets.interaction.show_inline_matplotlib_plots()
                    nite += 1

                await asyncio.sleep(0.01)
                if not start.value:
                    break
            start.description = 'Start'
            start.button_style = 'success'
            pause.disabled = True

        sol = None

        def start_simulation(change):
            if start.value:
                start.description = 'Stop'
                start.button_style = 'danger'
                pause.disabled = False
                simu_cfg = test_case.value.get_dictionary()
                param = simu_cfg['parameters']
                simu_cfg.update(lb_scheme.value.get_dictionary())
                param.update(simu_cfg['parameters'])
                simu_cfg['parameters'] = param
                simu_cfg['space_step'] = discret['dx'].value

                bound_cfg = {}
                bound_tc = test_case.value.get_boundary()
                bound_sc = lb_scheme.value.get_boundary()
                for key, val in bound_tc.items():
                    bound_cfg[key] = bound_sc[val]

                simu_cfg.pop('dim')
                simu_cfg['boundary_conditions'] = bound_cfg

                sol = pylbm.Simulation(simu_cfg)
                asyncio.ensure_future(run_simu(sol))
            else:
                start.description = 'Start'
                start.button_style = 'success'

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

