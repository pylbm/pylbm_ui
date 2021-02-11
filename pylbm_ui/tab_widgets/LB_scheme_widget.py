from ipywidgets import Dropdown, Output, VBox, Layout, Tab, Accordion, GridspecLayout, HTML, interaction
import markdown
import mdx_mathjax
from IPython.display import display, Markdown
import IPython.display as ipydisplay
from ..utils import schema_to_widgets

class LB_scheme_widget:

    def __init__(self, cases, default_case):
        default_layout = Layout(width='100%')
        self.case = Dropdown(
            options=cases,
            value=default_case,
            disabled=False,
            layout=default_layout
        )

        self.case_parameters = schema_to_widgets(self.case.value)

        param_widget = VBox([*self.case_parameters.values()])

        left_panel = VBox([HTML(value='<u><b>Select the LBM scheme</u></b>'),
                           self.case,
                           Accordion(children=[param_widget],
                                     _titles={0: 'Show parameters'},
                                     selected_index=None,
                                     layout=default_layout)],
                           layout=Layout(align_items='center', margin= '10px')
        )

        right_panel = Tab([Output(), Output(), Output()],
                          _titles= {0: 'Description',
                                    1: 'Properties',
                                    2: 'Equivalent equations'
                          },
        )

        def update_right_panel():
            md_desc = markdown.markdown(self.case.value.description)
            self.data = [ipydisplay.HTML(md_desc),
                         self.case.value.get_information(),
                         self.case.value.get_eqpde(),
            ]
            for i, d in enumerate(self.data):
                with right_panel.children[i]:
                    right_panel.children[i].clear_output()
                    display(d)

        def observer_param(change):
            for k, v in self.case_parameters.items():
                setattr(self.case.value, k, v.value)

        for c in self.case_parameters.values():
            c.observe(observer_param, 'value')

        def change_case(change):
            self.case_parameters = schema_to_widgets(self.case.value)
            param_widget.children = [*self.case_parameters.values()]
            for c in self.case_parameters.values():
                c.observe(observer_param, 'value')
            update_right_panel()

        self.case.observe(change_case, 'value')

        update_right_panel()

        self.widget = GridspecLayout(1, 4)
        self.widget[0, 0] = left_panel
        self.widget[0, 1:] = right_panel
