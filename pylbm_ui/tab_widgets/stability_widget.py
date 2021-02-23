from ipywidgets import Dropdown, Output, VBox, Layout, Tab, Accordion, GridspecLayout, HTML, Button
import markdown
import mdx_mathjax
from IPython.display import display, Markdown
import IPython.display as ipydisplay
import matplotlib.pyplot as plt
import numpy as np
from ..utils import schema_to_widgets

def prepare_stab_plot():
    plt.ioff()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    fig.canvas.header_visible = False
    fig.canvas.toolbar_visible = False

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
    return fig.canvas, markers1, markers2

class stability_widget:

    def __init__(self, test_case_widget, LB_scheme_widget):
        default_layout = Layout(width='100%')

        case = LB_scheme_widget.case
        case_parameters = LB_scheme_widget.case_parameters

        test_case = test_case_widget.case

        param_widget = VBox([*case_parameters.values()])

        left_panel = VBox([HTML(value='<u><b>Parameters</u></b>'),
                           Accordion(children=[param_widget],
                                     _titles={0: 'Scheme'},
                                     selected_index=None,
                                     layout=default_layout)],
                           layout=Layout(align_items='center', margin='10px')
        )

        state = Dropdown(options=test_case.value.state(),
                         layout=Layout(width='auto'),
        )

        stab_button = Button(description='>>> Click here to eval stability <<<',
                             button_style='warning',
                             layout=Layout(width='auto'),
        )

        stab_state = Button(disabled=True, layout=Layout(width='100%'))
        stab_state.layout.visibility = 'hidden'

        stab_output, markers1, markers2 = prepare_stab_plot()

        test_case_tab = VBox([HTML('<b>''Compute the linear stability for all the predefined physical states of the selected test case:'),
                         state,
                         HTML('Return UNSTABLE if at least ONE of the states is unstable'),
                         stab_button,
                         VBox([stab_state, stab_output]),
                         ],
                         layout=Layout(width='100%', align_items='center')
        )

        right_panel = Tab([test_case_tab, Output()],
                          _titles= {0: 'Test case states',
                                    1: 'User defined state',
                          },
        )

        def on_button_clicked(b):
            stab_state.layout.visibility = 'visible'
            stab_state.description = 'Compute eigenvalues ...'
            stab_state.button_style = 'warning'
            for k, v in case_parameters.items():
                setattr(case.value, k, v.value)

            stability = case.value.get_stability(state.value, markers1, markers2)
            stab_output.draw_idle()
            if stability.is_stable_l2:
                stab_state.description = 'STABLE for this physical state'
                stab_state.button_style = 'success'
            else:
                stab_state.description = 'UNSTABLE for the user defined physical state'
                stab_state.button_style = 'danger'

        def change_test_case(change):
            state.options = test_case.value.state()
            stab_state.layout.visibility = 'hidden'
            stab_output.clear_output()

        def change_case(change):
            case_parameters = schema_to_widgets(case.value)
            param_widget.children = [*case_parameters.values()]

        case.observe(change_case, 'value')
        test_case.observe(change_test_case, 'value')
        stab_button.on_click(on_button_clicked)

        self.widget = GridspecLayout(1, 4)
        self.widget[0, 0] = left_panel
        self.widget[0, 1:] = right_panel
