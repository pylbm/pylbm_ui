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
import json
import numpy as np
import time

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

        self.stats = {}
        ##
        ## The menu
        ##

        # configure the default simulation name
        self.simulation_name = v.TextField(
            label='Simulation name', v_model=''
        )
        self.update_name(None)

        self.simu_cfg = v.Select(label='Load simulation configuration', items=[], v_model=None)
        self.update_simu_cfg_list()

        self.discret = DiscretizationWidget(test_case_widget, lb_scheme_widget)

        self.codegen = v.Select(items=['auto', 'numpy', 'cython'], v_model='auto')

        self.save_fields = Save_widget(
            list(lb_scheme_widget.get_case().equation.get_fields().keys())
        )

        self.menu = [
            self.simulation_name,
            self.simu_cfg,
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

        self.period = StrictlyPositiveIntField(
            label='Period',
            v_model=round(self.discret['nt'].value / nb_split_period)
        )
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
        self.simu_cfg.observe(self.load_simu_cfg, 'v_model')
        self.discret['nt'].observe(self.change_period_by_nt, 'v_model')

        test_case_widget.select_case.observe(self.stop_simulation, 'v_model')
        lb_scheme_widget.select_case.observe(self.stop_simulation, 'v_model')
        lb_scheme_widget.select_case.observe(self.update_result, 'v_model')
        test_case_widget.select_case.observe(self.update_name, 'v_model')
        lb_scheme_widget.select_case.observe(self.update_name, 'v_model')

    def change_period_by_nt(self, change):
        """
        change de period of plot when the number of time steps is modified
        """
        if not self.discret['nt'].error:
            self.period.v_model = round(
                self.discret['nt'].value/nb_split_period
            )

    def update_simu_cfg_list(self):
        simu_list = []
        for root, d_names,f_names in os.walk(default_path):
                if 'simu_config.json' in f_names:
                    simu_list.append(os.path.join(root, 'simu_config.json'))
        simu_list.sort()
        self.simu_cfg.items = simu_list

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

        sol = self.simu.sol
        if sol:
            self.stats['MLUPS'] = sol.nt*np.prod(sol.domain.shape_in)/self.stats['LBM']/1e6
        self.simu.save_stats(self.stats)

    def update_result(self, change):
        """
        When the test case is changed, the equation can be changed giving
        new field outputs.

        This method updates the list in the menu accordingly.
        """
        self.simu.reset_fields(self.lb_scheme_widget.get_case().equation.get_fields())
        self.result.items = list(self.simu.fields.keys())
        self.result.v_model = list(self.simu.fields.keys())[0]
        self.save_fields.purge()
        self.save_fields.update_fields(list(self.lb_scheme_widget.get_case().equation.get_fields().keys()))

    def update_name(self, change):
        """
        When the test case or the scheme is changed,
        the default name of the simulation is updated
        """
        test_case = self.test_case_widget.get_case()
        lb_case = self.lb_scheme_widget.get_case()
        simu_name = f"{test_case.name}"
        simu_name += f"_{lb_case.name}_0"
        self.simulation_name.v_model = simu_name

    # def run_simu(self):
    async def run_simu(self):
        """
        Run the simulation asynchronously.
        """
        while self.dialog.v_model:
            await asyncio.sleep(0.01)

        if not self.dialog.replace:
            self.stop_simulation(None)
            return

        self.plot_output.children = [Message('Prepare the simulation')]

        v_model = {
            'model': self.test_case_widget.model.select_model.v_model,
            'test_case': self.test_case_widget.select_case.v_model,
            'lb_scheme': self.lb_scheme_widget.select_case.v_model,
        }
        test_case = self.test_case_widget.get_case()
        lb_scheme = self.lb_scheme_widget.get_case()

        self.simu.reset_path(
            os.path.join(default_path, self.simulation_name.v_model)
        )
        self.simu.reset_sol(
            v_model,
            test_case, lb_scheme,
            self.discret['dx'].value,
            self.codegen.v_model
        )
        self.simu.save_config()

        self.plot = Plot()
        self.iplot = 0
        self.plot_output.children = [self.plot.fig.canvas]

        self.simu.save_data(self.result.v_model)
        self.simu.plot(self.plot, self.result.v_model)
        self.plot_output.children[0].draw_idle()

        ite_to_save = self.save_fields.get_save_time(
            self.simu.sol.dt, self.simu.duration
        )

        nite = 1
        stop_time = self.simu.duration - .5*self.simu.sol.dt

        await asyncio.sleep(0.01)
        while self.simu.sol.t < stop_time:
            self.progress_bar.value = float(
                self.simu.sol.t
            )/self.simu.duration*100

            if not self.pause.v_model:

                if not self.period.error:
                    if nite > self.period.value:
                        nite = 1
                        self.simu.save_data(self.result.v_model)
                        self.simu.plot(self.plot, self.result.v_model)
                        self.plot_output.children[0].draw_idle()
                        ###### await asyncio.sleep(0.2)

                if self.simu.sol.nt in ite_to_save:
                    self.simu.save_data(ite_to_save[self.simu.sol.nt])

                t1 = time.time()
                self.simu.sol.one_time_step()
                t2 = time.time()
                self.stats['LBM'] += t2 - t1

                nite += 1
                self.iplot += 1

            if self.simu.sol.dim == 1:
                await asyncio.sleep(0.001)
            else:
                await asyncio.sleep(0)
            if self.start.v_model:
                break

        # save and plot the last time step
        if nite > 1:
            self.simu.save_data(self.result.v_model)
            self.simu.plot(self.plot, self.result.v_model)
            self.plot_output.children[0].draw_idle()

        # stop the simulation
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

            self.stats = {'LBM': 0}
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

    def load_simu_cfg(self, change):
        cfg = json.load(open(self.simu_cfg.v_model))

        self.test_case_widget.model.select_category.v_model = f'Dimension{cfg["dim"]}'
        self.test_case_widget.model.select_model.v_model = cfg['v_model']['model']
        self.test_case_widget.select_case.v_model = cfg['v_model']['test_case']
        self.lb_scheme_widget.select_case.v_model = cfg['v_model']['lb_scheme']

        self.discret['dx'].value =  cfg['dx']

        case = self.test_case_widget.get_case()
        param = self.test_case_widget.parameters
        for k, v in cfg['test_case']['args'].items():
            if k in param:
                param[k].value = v

        case = self.lb_scheme_widget.get_case()
        param = self.lb_scheme_widget.parameters
        for k, v in cfg['lb_scheme']['args'].items():
            if k in param:
                param[k].value = v

        if cfg['extra_config'] is not None:
            for k, v in cfg['extra_config'].items():
                key = k
                if k == 'lambda':
                    key = 'la'
                if key in param:
                    param[key].value = v
