# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v
from traitlets import Unicode
import ipywidgets as widgets
import IPython.display as ipydisplay

from .message import Message

out = widgets.Output()


def debug_widget(f):
    def wrapper(*args, **kwargs):
        with out:
            return f(*args, **kwargs)
    return wrapper


class PylbmWidget(v.VuetifyWidget):
    """
    Custom vuetifyWidget to add specific methods
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.viz = True
        self.old_class = ''

    def toggle_viz(self):
        """
        toogle the visibility of the widget

        Return:
            self
        """

        return self.hide() if self.viz else self.show()

    def hide(self):
        """
        Hide the widget by adding the d-none html class to the widget.
        Save the previous class and set viz attribute to False.

        Return:
            self
        """

        if 'd-none' not in str(self.class_):
            self.old_class = self.class_
            self.class_ = 'd-none'

        self.viz = False

        return self

    def show(self):
        """
        Hide the widget by removing the d-none html class to the widget
        Save the previous class and set viz attribute to True.

        Return:
            self
        """

        if self.old_class:
            self.class_ = self.old_class

        if 'd-none' in str(self.class_):
            self.class_ = str(self.class_).replace('d-none', '')

        self.viz = True

        return self


class ParametersPanel(PylbmWidget, v.ExpansionPanel):
    def __init__(self, title, **kwargs):
        super().__init__(
            children=[
                v.ExpansionPanelHeader(children=[title]),
                v.ExpansionPanelContent(children=[])
            ],
            **kwargs
        )
        self.data = None

    def update(self, data):
        self.children[1].children = list(data)

    def bind(self, method):
        for param in self.children[1].children:
            param.observe(method, 'v_model')

    def unbind(self, method):
        for param in self.children[1].children:
            param.unobserve(method, 'v_model')


class Container(PylbmWidget, v.Container):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs
        )


class HTML(v.Layout):
    """
    Custom Layout based on the html text given

    Args:
        html_str (str): the text to display using html format
    """

    def __init__(self, html_str="", **kwargs):

        self.out = widgets.Output()
        self.update_content(html_str)

        super().__init__(
            row=True,
            align_center=True,
            class_="pa-5 ma-2",
            children=[v.Flex(xs12=True, children=[self.out])],
            **kwargs
        )

    def update_content(self, html_str):

        with self.out:
            self.out.clear_output()
            ipydisplay.display(ipydisplay.HTML(html_str))

class Tooltip(v.Tooltip):
    def __init__(self, widget, tooltip, *args, activate=True, **kwargs):
        self.bottom = True
        self.v_slots = [
            {
                'name': 'activator',
                'variable': 'tooltip',
                'children': widget
            }
        ]
        widget.v_on = 'tooltip.on'

        self.children = [tooltip]

        super().__init__(*args, **kwargs)
