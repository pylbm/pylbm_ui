from ipywidgets import Dropdown, Output, VBox, Layout, Tab, Accordion, GridspecLayout, HTML, interaction
import markdown
import IPython.display as ipydisplay

from ..utils import schema_to_widgets

class test_case_widget:

    def __init__(self, cases, default_case):
        self.case = Dropdown(options=cases,
                             value=default_case,
                             disabled=False,
                             layout=Layout(width='auto')
        )

        self.case_parameters = schema_to_widgets(self.case.value)

        param_widget = VBox([*self.case_parameters.values()])

        left_panel = VBox([HTML(value='<u><b>Select the test case</u></b>'),
                           self.case,
                           Accordion(children=[param_widget],
                                     _titles={0: 'Show parameters'},
                                     selected_index=None,
                                     layout=Layout(width='100%'))],
                           layout=Layout(align_items='center', margin='10px')
        )

        right_panel = Tab([Output(), Output()],
                          _titles= {0: 'Description',
                                    1: 'Reference results'
                          },
        )

        def update_right_panel():
            with right_panel.children[0]:
                right_panel.children[0].clear_output()
                display(ipydisplay.HTML(markdown.markdown(self.case.value.description)))

            interaction.show_inline_matplotlib_plots()
            with right_panel.children[1]:
                right_panel.children[1].clear_output()
                self.plot_exact_solution()
                interaction.show_inline_matplotlib_plots()

        def observer(change):
            update_right_panel()

        for c in self.case_parameters.values():
            c.observe(observer, 'value')

        def change_case(change):
            self.case_parameters = schema_to_widgets(self.case.value)
            param_widget.children = [*self.case_parameters.values()]
            for c in self.case_parameters.values():
                c.observe(observer, 'value')
            observer(None)

        self.case.observe(change_case, 'value')

        update_right_panel()

        self.widget = GridspecLayout(1, 4)
        self.widget[0, 0] = left_panel
        self.widget[0, 1:] = right_panel

    def plot_exact_solution(self):
        for k, v in self.case_parameters.items():
            setattr(self.case.value, k, v.value)
        self.case.value.plot_ref_solution()