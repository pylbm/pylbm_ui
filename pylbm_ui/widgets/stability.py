# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v
import matplotlib.pyplot as plt
import numpy as np

from ..utils import schema_to_widgets, FloatField
from .pylbmwidget import Container
from .dialog_form import Form, Item, Dialog, add_rule
from .debug import debug

def print_state(state):
    if 'name' in state:
        s = f"{state['name']}: "
    else:
        s = ''
    s += ', '.join([f'{str(k)} = {v}' for k, v in state.items() if k != 'name'])
    return s

@debug
class StateForm(Form):
    def __init__(self, state, **kwargs):
        """
        Define a form to create a new state used for the linear stability.

        Parameter
        =========

        state: dict
            The keys are the name of input text field.
            The values are the default values for these text fields.

        """
        self.update_state(state)
        super().__init__(v_model='valid', children=self.fields)

    def update_state(self, state):
        """
        Create a FloatField for each key and add them to the form.
        """
        self.state = state.copy()
        if 'name' in self.state:
            self.state.pop('name')

        self.fields = []
        for k, v in self.state.items():
            self.fields.append(FloatField(label=str(k), v_model=v))
        self.children = self.fields

    def get_form_state(self):
        """
        Return the state from the values entered in the form.
        """
        for i, k in enumerate(self.state.keys()):
            self.state[k] = self.fields[i].value
        return self.state

@debug
class StateItem(Item):
    form_class = StateForm
    update_text = 'Update linear state configuration'

    def __init__(self, state, remove=True, **kwargs):
        """
        Create a state item from the default states defined by the test case
        or by those defined by the user.

        This state item is then added into a v.List and can be clicked to modify
        its values using a dialog box.

        Parameters
        ==========

        state: dict
            the state used to create a state item.

        remove: bool
            add a remove button if yes.

        """
        self.state = state.copy()
        super().__init__(state, **kwargs)

        self.content.children = [f'{self}']

        # add a remove button if state defined by the user
        if remove:
            action = v.ListItemAction(children=[self.btn])
        else:
            action = v.ListItemAction(children=[])

        self.stab_status = v.Card(children=['uncheck'], class_='pa-2')

        self.children=[
            action,
            v.ListItemContent(
            children=[
                v.Card(children=[self.content],
                        flat=True,
                        color='transparent',
                        light=True,
                ),
            self.update_dialog
            ]),
            v.ListItemAction(children=[self.stab_status])
        ]

    def update_click(self, widget, event, data):
        """
        Used when the item is clicked into the list view.
        """
        super().update_click(widget, event, data)
        self.stab_status.children = ['uncheck']
        self.stab_status.color = None

    def form2field(self):
        """
        Put the values of the update form into the state.
        """
        for i, k in enumerate(self.state.keys()):
            self.state[k] = self.form.fields[i].value

    def field2form(self):
        """
        Put the values of the state into the update form.
        """
        for i, k in enumerate(self.state.keys()):
            self.form.fields[i].value = self.state[k]

    def __str__(self):
        return print_state(self.state)

@debug
class StateWidget(Dialog):
    item_class = StateItem
    new_text = "New linear state configuration"

    def __init__(self, states):
        """
        Create a list of state items and a plus button to add new states.

        Parameter
        =========

        states: list
            The list of default states defined by the test case.

        """
        self.states = states
        self.default_state = self.states[0]
        super().__init__(self.default_state)

        self.eval_stab = v.Btn(children=['Check stability'], color='primary')

        for s in states:
            self.item_list.children.append(self.create_item(s))

        self.item_list.notify_change({'name': 'children', 'type': 'change'})

        self.widget = v.Card(children=[
            v.CardTitle(children=['List of linear states', v.Spacer(), self.add_button]),
            v.CardText(children=[self.item_list]),
            v.CardActions(children=[v.Spacer(), self.eval_stab])
        ])

    def create_item(self, state=None):
        """
        Create a new state item into the list.

        Parameter
        =========

        state: dict
            use this state if it's not None, otherwise take the values given by the form.

        """
        remove = False
        if state is None:
            state = self.form.get_form_state()
            remove = True

        return self.item_class(state, remove,
                    class_='ma-1',
                    style_='background-color: #F8F8F8;'
        )

    def update_states(self, states):
        """
        When the test case changed, clean the list and add the new states.

        Parameter
        ========

        states: list
            list of the states of the test case.

        """
        self.item_list.children = []
        for s in states:
            self.item_list.children.append(self.create_item(s))

        # Take the values of the first state as the default values for the add item form
        self.form.update_state(states[0])
        self.item_list.notify_change({'name': 'children', 'type': 'change'})

    def get_states(self):
        """
        Return all the states found into the list.
        """
        states = []
        for state in self.item_list.children:
            states.append(state.state)
        return states

def prepare_stab_plot():
    """
    Prepare the plot of the linear stability study.
    """
    plt.ioff()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    fig.canvas.header_visible = False

    ax1.axis([-1.1, 1.1, -1.1, 1.1])
    ax1.grid(visible=False)
    ax1.set_xlabel('real part')
    ax1.set_ylabel('imaginary part')
    ax1.set_xticks([-1, 0, 1])
    ax1.set_xticklabels([r"$-1$", r"$0$", r"$1$"])
    ax1.set_yticks([-1, 0, 1])
    ax1.set_yticklabels([r"$-1$", r"$0$", r"$1$"])
    theta = np.linspace(0, 2*np.pi, 1000)
    ax1.plot(np.cos(theta), np.sin(theta), alpha=0.5, color='navy')

    ax2.axis([0, 2*np.pi, -0.1, 1.1])
    ax2.grid(visible=True)
    ax2.set_xlabel('wave vector modulus')
    ax2.set_ylabel('modulus')
    ax2.set_xticks([k*np.pi/4 for k in range(0, 9)])
    ax2.set_xticklabels(
        [
            r"$0$", r"$\frac{\pi}{4}$", r"$\frac{\pi}{2}$",
            r"$\frac{3\pi}{4}$", r"$\pi$",
            r"$\frac{5\pi}{4}$", r"$\frac{3\pi}{2}$",
            r"$\frac{7\pi}{4}$", r"$2\pi$"
        ]
    )
    ax2.plot([0, 2*np.pi], [1., 1.], alpha=0.5, color='navy')

    markers1 = ax1.scatter(0, 0, c='orange', s=0.5, alpha=0.5)
    markers2 = ax2.scatter(0, 0, c='orange', s=0.5, alpha=0.5)
    return fig, markers1, markers2

@debug
class StabilityWidget:
    def __init__(self, test_case_widget, lb_scheme_widget):
        """
        Widget definition for linear stability of a lattice Boltzmann scheme.

        Parameters
        ==========

        - test_case_widget:
            widget of the test case (see test_case.py).

        - lb_scheme_widget:
            widget of the lattice Boltzmann scheme (see lb_scheme.py).

        This widget is composed by a menu where you can modify the parameters of the
        lattice Boltzmann scheme.

        This widget is also composed by a main widget where the linear stability for the
        states provided by the test case can be tested to check their stability. A user can
        add its own states. A second tab allows to plot the stability region of a given state.

        """
        self.test_case_widget = test_case_widget
        self.lb_scheme_widget = lb_scheme_widget

        ##
        ## The menu
        ##
        self.menu = [self.lb_scheme_widget.panels]

        ##
        ## The main
        ##

        # Tab 1
        test_case = self.test_case_widget.get_case()
        self.state_widget = StateWidget(test_case.state())
        tab1 = v.TabItem(children=[self.state_widget.widget],
                         class_="ma-6")

        # Tab 2
        self.state_list = v.Select(label='States', items=[], v_model=0)

        plot_stab = v.Btn(children=['Plot stability region'], color='primary')
        self.alert = v.Alert(children=['Check the stability for this state...'], dense=True, type='info')
        self.stab_output, self.markers1, self.markers2 = prepare_stab_plot()

        self.container = Container(children=[v.Row(children=[v.Col(children=[self.alert])]),
                                             v.Row(children=[self.stab_output.canvas], align='center', justify='center')],
                                   align_content_center=True,)
        self.container.hide()

        tab2 = v.TabItem(children=[
            v.Card(children=[
                v.CardTitle(children=['Plot the linear stability for a given state']),
                v.CardText(children=[
                    v.Row(children=[
                        v.Col(children=[self.state_list], md=9, sm=12),
                        v.Col(children=[plot_stab], md=3, sm=12),
                        ],
                        align='center',
                        justify='space-around'
                    ),
                    self.container
                ]),
            ],
            class_="ma-6",
            )]
        )

        # main
        tabs = v.Tabs(v_model=None,
                      children=[v.Tab(children=['Check stability']),
                                v.Tab(children=['Plot stability region']),
                                tab1,
                                tab2
                      ])

        self.main = [tabs]

        self.update_states(None)
        self.change_test_case(None)

        ##
        ## Widget events
        ##
        self.test_case_widget.select_case.observe(self.change_test_case, 'v_model')
        self.test_case_widget.select_case.observe(self.hide_plot, 'v_model')
        self.lb_scheme_widget.select_case.observe(self.hide_plot, 'v_model')

        self.state_widget.eval_stab.on_event('click', self.stability_states)
        self.state_widget.item_list.observe(self.update_states, 'children')

        plot_stab.on_event('click', self.plot_stability)

    def stability_states(self, widget, event, data):
        """
        Check the stability of each state and change their status button.
        """
        for state in self.state_widget.item_list.children:
            # test_case = self.test_case_widget.get_case()
            case = self.lb_scheme_widget.get_case()
            stability = case.get_stability(state.state)
            if stability.is_stable_l2:
                state.stab_status.children = ['stable']
                state.stab_status.color = 'success'
            else:
                state.stab_status.children = ['unstable']
                state.stab_status.color = 'error'

    def plot_stability(self, widget, event, data):
        """
        Plot the stability region of the selected state.
        """
        if not self.container.viz:
            self.container.show()

        if self.state_list.v_model is not None:
            self.markers1.set_offsets([])
            self.markers2.set_offsets([])
            self.stab_output.canvas.draw_idle()

            self.alert.type = 'info'
            self.alert.children = ['Check the stability for this state...']
            test_case = self.test_case_widget.get_case()
            case = self.lb_scheme_widget.get_case()
            state = self.state_widget.get_states()[self.state_list.v_model]
            stability = case.get_stability(state, self.markers1, self.markers2)
            self.stab_output.canvas.draw_idle()
            if stability.is_stable_l2:
                self.alert.type = 'success'
                self.alert.children = ['STABLE for this physical state']
            else:
                self.alert.type = 'error'
                self.alert.children = ['UNSTABLE for this physical state']

    def change_test_case(self, change):
        """
        Update the states when the test case is changed or its parameters.
        """
        test_case = self.test_case_widget.get_case()
        self.state_widget.update_states(test_case.state())
        self.test_case_widget.panels.children[0].bind(self.change_test_case)

    def update_states(self, change):
        """
        Update the state lists for the stability region plot.
        """
        self.state_list.items = [{'text':print_state(s), 'value': i} for i, s in enumerate(self.state_widget.get_states())]
        self.state_list.v_model = 0

    def hide_plot(self, change):
        """
        Hide the stability region plot.
        """
        self.container.hide()

