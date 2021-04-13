import ipyvuetify as v
import matplotlib.pyplot as plt
import numpy as np

from ..utils import schema_to_widgets, FloatField
from .pylbmwidget import Markdown, ParametersPanel, Tabs, out, Container

from .dialog_form import Form, Item, Dialog, add_rule

class StateForm(Form):
    def __init__(self, state, **kwargs):
        self.state = state.copy()
        self.fields = []
        for k, v in state.items():
            self.fields.append(FloatField(label=str(k), v_model=v))

        super().__init__(v_model='valid', children=self.fields)

    def get_form_state(self):
        for i, k in enumerate(self.state.keys()):
            self.state[k] = self.fields[i].value
        return self.state

class StateItem(Item):
    form_class = StateForm
    update_text = 'Update linear state configuration'

    def __init__(self, state, remove=True, **kwargs):
        with out:
            self.state = state.copy()
            super().__init__(state, **kwargs)
            self.content.children = [f'{self}']

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
        super().update_click(widget, event, data)
        self.stab_status.children = ['uncheck']
        self.stab_status.color = None

    def form2field(self):
        for i, k in enumerate(self.state.keys()):
            self.state[k] = self.form.fields[i].value

    def field2form(self):
        for i, k in enumerate(self.state.keys()):
            self.form.fields[i].value = self.state[k]

    def __str__(self):
        return ', '.join([f'{str(k)} = {v}' for k, v in self.state.items()])

class StateWidget(Dialog):
    item_class = StateItem
    new_text = "New linear state configuration"

    def __init__(self, states):
        with out:
            self.states = states
            self.default_state = self.states[0]
            print('dafault state', self.default_state)
            super().__init__(self.default_state)

            self.eval_stab = v.Btn(children=['Check stability'], color='primary')

            for s in states:
                self.item_list.children.append(self.create_item(s))

            self.item_list.notify_change({'name': 'children', 'type': 'change'})

            self.widget = v.Card(children=[
                v.CardTitle(children=['List of linear states']),
                v.CardText(children=[self.item_list]),
                v.CardActions(children=[v.Spacer(), self.eval_stab, self.add_button])
            ])

    def create_item(self, state=None):
        with out:
            remove = False
            if state is None:
                state = self.form.get_form_state()
                remove = True

            return self.item_class(state, remove,
                        class_='ma-1',
                        style_='background-color: #F8F8F8;'
            )

    def update_states(self, states):
        self.item_list.children = []
        for s in states:
            self.item_list.children.append(self.create_item(s))
        self.item_list.notify_change({'name': 'children', 'type': 'change'})

    def get_states(self):
        states = []
        for state in self.item_list.children:
            states.append(state.state)
        return states

def prepare_stab_plot():
    plt.ioff()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    fig.canvas.header_visible = False

    ax1.axis([-1.1, 1.1, -1.1, 1.1])
    ax1.grid(visible=False)
    ax1.set_label(['real part', 'imaginary part'])
    ax1.set_xticks([-1, 0, 1])
    ax1.set_xticklabels([r"$-1$", r"$0$", r"$1$"])
    ax1.set_yticks([-1, 0, 1])
    ax1.set_yticklabels([r"$-1$", r"$0$", r"$1$"])
    theta = np.linspace(0, 2*np.pi, 1000)
    ax1.plot(np.cos(theta), np.sin(theta), alpha=0.5, color='navy')

    ax2.axis([0, 2*np.pi, -0.1, 1.1])
    ax2.grid(visible=True)
    ax2.set_label(['wave vector modulus', 'modulus'])
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

class stability_widget:
    def __init__(self, test_case_widget, LB_scheme_widget):
        case = LB_scheme_widget.get_case()
        panels = LB_scheme_widget.panels

        test_case = test_case_widget.get_case()
        state_list = v.Select(label='States', items=[], v_model=0)

        plot_stab = v.Btn(children=['Plot stability region'], color='primary')
        alert = v.Alert(children=['Check the stability for this state...'], dense=True, type='info')
        stab_output, markers1, markers2 = prepare_stab_plot()

        container = Container(children=[v.Row(children=[v.Col(children=[alert])]),
                                        v.Row(children=[stab_output.canvas], align='center', justify='center')],
                                align_content_center=True,)
        container.hide()

        state_widget = StateWidget(test_case.state())

        tabs_content = [v.TabItem(children=[state_widget.widget]),
                        v.TabItem(children=[
                            v.Card(children=[v.CardTitle(children=['Plot the linear stability for a given state']),
                                             v.CardText(children=[v.Row(children=[state_list, plot_stab]),
                                                                  container]),
                                            ],
                            class_="ma-6",
                            elevation=10)]),
        ]
        tabs = Tabs(v_model=None,
                    children=[v.Tab(children=['Check stability']),
                              v.Tab(children=['Plot stability region'])] + tabs_content)

        def stability_states(widget, event, data):
            for state in state_widget.item_list.children:
                test_case = test_case_widget.get_case()
                case = LB_scheme_widget.get_case()
                stability = case.get_stability(state.state)
                if stability.is_stable_l2:
                    state.stab_status.children = ['stable']
                    state.stab_status.color = 'success'
                else:
                    state.stab_status.children = ['unstable']
                    state.stab_status.color = 'error'

        def plot_stability(widget, event, data):
            if not container.viz:
                container.show()

            if state_list.v_model is not None:
                markers1.set_offsets([])
                markers2.set_offsets([])
                stab_output.canvas.draw_idle()

                alert.type = 'info'
                alert.children = ['Check the stability for this state...']
                test_case = test_case_widget.get_case()
                case = LB_scheme_widget.get_case()
                state = state_widget.get_states()[state_list.v_model]
                stability = case.get_stability(state, markers1, markers2)
                stab_output.canvas.draw_idle()
                if stability.is_stable_l2:
                    alert.type = 'success'
                    alert.children = ['STABLE for this physical state']
                else:
                    alert.type = 'error'
                    alert.children = ['UNSTABLE for this physical state']

        plot_stab.on_event('click', plot_stability)
        state_widget.eval_stab.on_event('click', stability_states)

        def change_test_case(change):
            test_case = test_case_widget.get_case()
            state_widget.update_states(test_case.state())

        def update_states(change):
            state_list.items = [{'text':str(s), 'value': i} for i, s in enumerate(state_widget.get_states())]
            state_list.v_model = 0

        def hide_plot(change):
            container.hide()

        update_states(None)
        state_widget.item_list.observe(update_states, 'children')

        test_case_widget.select_case.observe(change_test_case, 'v_model')
        test_case_widget.select_case.observe(hide_plot, 'v_model')
        LB_scheme_widget.select_case.observe(hide_plot, 'v_model')

        self.widget = v.Row(children=[v.Col(children=[panels], sm=3),
                                      v.Col(children=[tabs])
        ])
        self.main = [tabs]
        self.menu = [panels]