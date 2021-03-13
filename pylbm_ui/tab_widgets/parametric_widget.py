import ipyvuetify as v
import markdown
import ipywidgets as widgets

from .design_space import Design_widget
from ..utils import required_fields

class parametric_widget:
    def __init__(self, test_case_widget, lb_scheme_widget):

        fields = required_fields(test_case_widget.get_case())
        fields.update(required_fields(lb_scheme_widget.get_case()))

        parameters = {'relaxation parameters': None}
        parameters.update({f: v['value'] for f, v in fields.items() if v['type'] != 'relaxation parameter'})
        relax_parameters = {f: v['value'] for f, v in fields.items() if v['type'] == 'relaxation parameter'}

        left_panel = v.ExpansionPanels(children=[
            v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(children=['Design space']),
                v.ExpansionPanelContent(children=[
                    Design_widget(parameters, relax_parameters).widget
                ]),
            ]),
            v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(children=['Responses']),
            ]),
            v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(children=['Methods']),
            ]),
        ], multiple=True)

        #
        # Right panel
        #

        start = v.Btn(v_model=True, children=['Start'], class_="ma-2", style_="width: 100px", color='success')
        pause = v.Btn(children=['Pause'], class_="ma-2", style_="width: 100px", disabled=True, v_model=False)
        progress_bar = v.ProgressLinear(height=20, value=0, color="light-blue", striped=True)
        plotly_plot = v.Layout()

        right_panel = [
            v.Row(children=[start, pause]),
            progress_bar,
            v.Row(children=[plotly_plot])
        ]

        self.widget = v.Row(children=[
            v.Col(children=[left_panel], sm=3),
            v.Col(children=right_panel)
        ])