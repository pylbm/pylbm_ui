from ipywidgets import Dropdown, Output, VBox, Layout, Tab, Accordion, GridspecLayout, HTML, Button
import markdown
import mdx_mathjax
from IPython.display import display, Markdown
import IPython.display as ipydisplay
from ..utils import schema_to_widgets

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

        stab_state = Button(disabled=True, layout=Layout(width='auto'))
        stab_state.layout.visibility = 'hidden'
        stab_output = Output()

        test_case_tab = VBox([HTML('<b>''Compute the linear stability for all the predefined physical states of the selected test case:'),
                         state,
                         HTML('Return UNSTABLE if at least ONE of the states is unstable'),
                         stab_button,
                         VBox([stab_state, stab_output]),
                         ],
                         layout=Layout(width='auto', align_items='center')
        )

        right_panel = Tab([test_case_tab, Output()],
                          _titles= {0: 'Test case states',
                                    1: 'User defined state',
                          },
        )

        def on_button_clicked(b):
            for k, v in case_parameters.items():
                setattr(case.value, k, v.value)
            with stab_output:
                stab_output.clear_output()
                stability = case.value.get_stability(state.value)
                if stability.is_stable_l2:
                    stab_state.description = 'STABLE for this physical state'
                    stab_state.button_style = 'success'
                else:
                    stab_state.description = 'UNSTABLE for the user defined physical state'
                    stab_state.button_style = 'danger'
            stab_state.layout.visibility = 'visible'

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
