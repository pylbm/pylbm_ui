from ipywidgets import HBox, VBox, GridspecLayout, Dropdown, Layout, Button, FloatProgress, Text, HTML, Accordion, SelectMultiple, Tab, Output, ToggleButton, IntText
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

        default_layout = Layout(width='100%')

        test_case = test_case_widget.case
        lb_scheme = lb_scheme_widget.case
        case_parameters = lb_scheme_widget.case_parameters

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
                                description='<b>field(s)</b>',
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

        left_panel = VBox([HTML(value='<u><b>Simulation name</u></b>'),
                           Text(value='simu',
                                layout=default_layout
                            ),
                           HTML(value='<u><b>Settings</u></b>'),
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
        )

        func = {}
        for k, v in fields.items():
            func[k] = sp.lambdify(v.atoms(sp.Symbol), v, "numpy", dummify=False)

        async def run_simu(sol):
            nite = 1
            to_subs = {str(k): sol.m[k] for k in sol.scheme.consm.keys()}
            to_subs.update({str(k): v for k, v in sol.scheme.param.items()})
            while True:
                progress.value = sol.t/test_case.value.duration
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

        def on_button_clicked(change):
            if start.value:
                start.description = 'Stop'
                start.button_style = 'danger'
                for k, v in case_parameters.items():
                    setattr(lb_scheme.value, k, v.value)
                simu_cfg = test_case.value.get_dictionary()
                param = simu_cfg['parameters']
                simu_cfg.update(lb_scheme.value.get_dictionary())
                param.update(simu_cfg['parameters'])
                simu_cfg['parameters'] = param

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

        start.observe(on_button_clicked, 'value')

        self.widget = VBox([HBox([start, progress]),
                            GridspecLayout(1, 4)])
        self.widget.children[1][0, 0] = left_panel
        self.widget.children[1][0, 1:] = right_panel

