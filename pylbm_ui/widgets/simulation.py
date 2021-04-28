# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import pylbm
import asyncio
import os
import ipyvuetify as v

from .discretization import DiscretizationWidget
from .save_widget import Save_widget
from .pylbmwidget import Tooltip
from .dialog_path import DialogPath
from ..config import default_path, nb_split_period
from ..simulation import simulation, Plot
from ..utils import StrictlyPositiveIntField, StrictlyPositiveFloatField
from .message import Message
from .debug import debug

@debug
class SimulationWidget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        """
        Widget definition for simulation of lattice Boltzmann methods.

        Parameters
        ==========

        - test_case_widget:
            widget of the test case (see test_case.py).

        - lb_scheme_widget:
            widget of the lattice Boltzmann scheme (see lb_scheme.py).

        This widget is composed by a menu where you can modify the discretization parameters,
        the generator used to build the numerical kernel into pylbm and the desired outputs for
        post treatment.

        This widget is also composed by a main widget where the simulation can be started and
        a plot is given in real time for the available fields. A period can be modified to control
        the plot frequency and a snapshot of the current figure can be made.

        """
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget
        test_case = test_case_widget.get_case()
        tc_param = test_case_widget.parameters
        lb_case = lb_scheme_widget.get_case()
        lb_param = lb_scheme_widget.parameters

        ##
        ## The menu
        ##

        self.simulation_name = v.TextField(label='Simulation name', v_model='simu_0')

        input_file = v.FileInput(label='Choose a simu_config.json', accept=".json")

        self.discret = DiscretizationWidget(test_case_widget, lb_scheme_widget)

        self.codegen = v.Select(items=['auto', 'numpy', 'cython'], v_model='auto')

        self.save_fields = Save_widget(list(lb_scheme_widget.get_case().equation.get_fields().keys()))

        self.menu = [
            self.simulation_name,
            input_file,
            v.ExpansionPanels(children=[
                self.discret,
                v.ExpansionPanel(children=[
                    v.ExpansionPanelHeader(children=['Code generator']),
                    v.ExpansionPanelContent(children=[self.codegen]),
                ]),
                v.ExpansionPanel(children=[
                    v.ExpansionPanelHeader(children=['Field output request']),
                    v.ExpansionPanelContent(children=[
                        self.save_fields.widget
                    ]),
                ]),
            ], multiple=True, class_='pa-0')
        ]

        ##
        ## The main
        ##

        self.simu = simulation()
        self.simu.reset_fields(lb_scheme_widget.get_case().equation.get_fields())

        self.start = v.Btn(v_model=True, children=['Start'], class_='ma-2', style_='width: 100px', color='success')
        self.startTooltip = Tooltip(self.start, tooltip='click to start the simulation')

        self.pause = v.Btn(children=['Pause'], class_='ma-2', style_='width: 100px', disabled=True, v_model=False)
        self.progress_bar = v.ProgressLinear(height=20, value=0, color='light-blue', striped=True)
        self.result = v.Select(items=list(self.simu.fields.keys()), v_model=list(self.simu.fields.keys())[0])
        self.period = StrictlyPositiveIntField(label='Period', v_model=self.discret['nt'].value/nb_split_period)
        self.snapshot = v.Btn(children=['Snapshot'])

        self.plot = Plot()
        self.iplot = 0
        self.plot_output = v.Row(justify='center')

        self.dialog = DialogPath()

        self.main = [
            v.Row(children=[
                self.startTooltip,
                Tooltip(self.pause, tooltip='click to pause the simulation'),
                self.dialog,
            ]),
            self.progress_bar,
            v.Row(children=[
                v.Col(children=[self.result], md=5, sm=12),
                v.Col(children=[self.period], md=5, sm=12),
                v.Col(children=[self.snapshot], md=2, sm=12),
            ], align='center', justify='space-around', ),
            self.plot_output,
        ]

        ##
        ## Widget events
        ##

        self.start.on_event('click', self.start_simulation)
        self.pause.on_event('click', self.on_pause_click)
        self.snapshot.on_event('click', self.take_snapshot)
        self.result.observe(self.replot, 'v_model')

        test_case_widget.select_case.observe(self.stop_simulation, 'v_model')
        lb_scheme_widget.select_case.observe(self.stop_simulation, 'v_model')
        lb_scheme_widget.select_case.observe(self.update_result, 'v_model')

    def stop_simulation(self, change):
        """
        When the stop button is clicked replace it by the start button
        and disable the pause button.
        """
        self.start.v_model = True
        self.start.children = ['Start']
        self.startTooltip.children = ['click to start the simulation']
        self.start.color = 'success'
        self.pause.disabled = True
        self.pause.v_model = False

    def update_result(self, change):
        """
        When the test case is changed, the equation can be changed giving
        new field outputs.

        This method updates the list in the menu accordingly.
        """
        self.simu.reset_fields(self.lb_scheme_widget.get_case().equation.get_fields())
        self.result.items = list(self.simu.fields.keys())
        self.result.v_model = list(self.simu.fields.keys())[0]

    async def run_simu(self):
    # def run_simu(self):
        """
        Run the simulation asynchronously.
        """
        while self.dialog.v_model:
            await asyncio.sleep(0.01)

        if not self.dialog.replace:
            self.stop_simulation(None)
            return

        nite = 1

        self.plot_output.children = [Message('Prepare the simulation')]

        test_case = self.test_case_widget.get_case()
        lb_scheme = self.lb_scheme_widget.get_case()

        self.simu.reset_path(os.path.join(default_path, self.simulation_name.v_model))
        self.simu.reset_sol(test_case, lb_scheme, self.discret['dx'].value, self.codegen.v_model)
        self.simu.save_config()

        self.plot = Plot()
        self.iplot = 0
        self.plot_output.children = [self.plot.fig.canvas]

        self.simu.plot(self.plot, self.result.v_model)
        self.plot_output.children[0].draw_idle()

        ite_to_save = self.save_fields.get_save_time(self.simu.sol.dt, self.simu.duration)

        await asyncio.sleep(0.01)
        while self.simu.sol.t <= self.simu.duration:
            self.progress_bar.value = float(self.simu.sol.t)/self.simu.duration*100

            if not self.pause.v_model:
                self.simu.sol.one_time_step()

                if not self.period.error:
                    if nite >= self.period.value:
                        nite = 1
                        self.simu.save_data(self.result.v_model)
                        self.simu.plot(self.plot, self.result.v_model)
                        self.plot_output.children[0].draw_idle()
                        # await asyncio.sleep(0.2)

                if self.simu.sol.nt in ite_to_save:
                    self.simu.save_data(ite_to_save[self.simu.sol.nt])

                nite += 1
                self.iplot += 1

            await asyncio.sleep(0.001)
            if self.start.v_model:
                break
        self.stop_simulation(None)

    def start_simulation(self, widget, event, data):
        """
        When the start button is clicked, check if the simulation path is empty,
        change the behavior of the button (start->stop), enable pause button, and
        run the simulation.
        """
        if self.start.v_model:
            simu_path = os.path.join(default_path, self.simulation_name.v_model)
            self.dialog.check_path(simu_path)

            self.start.v_model = False
            self.start.children = ['Stop']
            self.start.color = 'error'

            self.pause.disabled = False
            self.progress_bar.value = 0

            asyncio.ensure_future(self.run_simu())
            # self.run_simu()
        else:
            self.stop_simulation(None)

    def on_pause_click(self, widget, event, data):
        """
        Pause the simulation when the pause button is clicked.
        """
        self.pause.v_model = not self.pause.v_model

    def replot(self, change):
        """
        Update the plot.
        """
        if self.plot:
            self.simu.plot(self.plot, self.result.v_model)
            self.plot_output.children[0].draw_idle()

    def take_snapshot(self, widget, event, data):
        """
        Take a snapshot of the current plot and save it into the
        the simulation path.
        """
        if self.plot:
            self.plot.fig.savefig(os.path.join(self.simu.path, f'snapshot_{self.result.v_model}_{self.iplot}.png'), dpi=300,  bbox_inches='tight')
