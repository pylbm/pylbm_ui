import ipyvuetify as v
import matplotlib.pyplot as plt
import numpy as np

from ..utils import schema_to_widgets
from .pylbmwidget import Markdown, ParametersPanel, Tabs, out, Container

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
        state = v.Select(label='States', items=[{'text':str(s), 'value': i} for i, s in enumerate(test_case.state())], v_model=0)

        eval_stab = v.Btn(children=['Check stability'], color='primary')
        alert = v.Alert(children=['Check the stability for this state...'], dense=True, type='info')
        stab_output, markers1, markers2 = prepare_stab_plot()

        container = Container(children=[v.Row(children=[v.Col(children=[alert])]),
                                        v.Row(children=[stab_output.canvas], align='center', justify='center')],
                                align_content_center=True,)
        container.hide()

        tabs_content = [v.TabItem(children=[v.Card(children=[v.CardTitle(children=['Compute the linear stability for all the predefined physical states of the selected test case:']),
                                             v.CardText(children=[state, 'Return UNSTABLE if at least ONE of the states is unstable']),
                                             v.CardActions(children=[v.Spacer(), eval_stab])
                                             ],
                                             class_="ma-6",
                                             elevation=10),
                                             container
        ])]
        tabs = Tabs(v_model=None, children=[v.Tab(children=['Test case states']),
                                            v.Tab(children=['User defined state'])] + tabs_content, right=True)

        def on_click(widget, event, data):
            with out:
                if not container.viz:
                    container.show()

                if state.v_model is not None:
                    markers1.set_offsets([])
                    markers2.set_offsets([])
                    stab_output.canvas.draw_idle()

                    alert.type = 'info'
                    alert.children = ['Check the stability for this state...']
                    test_case = test_case_widget.get_case()
                    case = LB_scheme_widget.get_case()
                    stability = case.get_stability(test_case.state()[state.v_model], markers1, markers2)
                    stab_output.canvas.draw_idle()
                    if stability.is_stable_l2:
                        alert.type = 'success'
                        alert.children = ['STABLE for this physical state']
                    else:
                        alert.type = 'error'
                        alert.children = ['UNSTABLE for this physical state']

        eval_stab.on_event('click', on_click)

        def change_test_case(change):
            test_case = test_case_widget.get_case()
            state.items = [{'text':str(s), 'value': i} for i, s in enumerate(test_case.state())]
            state.v_model = 0

        def hide_plot(change):
            container.hide()

        test_case_widget.select_case.observe(change_test_case, 'v_model')
        test_case_widget.select_case.observe(hide_plot, 'v_model')
        LB_scheme_widget.select_case.observe(hide_plot, 'v_model')

        self.widget = v.Row(children=[v.Col(children=[panels], sm=3),
                                      v.Col(children=[tabs])
        ])
