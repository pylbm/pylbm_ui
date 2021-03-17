import ipyvuetify as v
from markdown import markdown
from traitlets import Unicode
import ipywidgets as widgets
import IPython.display as ipydisplay

out = widgets.Output()

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

        if not 'd-none' in str(self.class_):
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
            children=[v.ExpansionPanelHeader(children=[title]),
                      v.ExpansionPanelContent(children=[])],
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

class Tabs(PylbmWidget, v.Tabs):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs
        )

class Container(PylbmWidget, v.Container):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs
        )

class Markdown(v.Layout):
    """
    Custom Layout based on the markdown text given

    Args:
        mkd_str (str): the text to display using the markdown convention. multi-line string are also interpreted
    """

    def __init__(self, mkd_str="", **kwargs):

        self.out = widgets.Output()

        mkd = markdown(mkd_str, extensions=['fenced_code','sane_lists', 'mdx_math'])
        with self.out:
            ipydisplay.display(ipydisplay.HTML(mkd))

        #create a Html widget
        # class MyHTML(v.VuetifyTemplate):
        #     template = Unicode(f'<div>{mkd}</div>').tag(sync=True)

        # self.content = MyHTML()

        super().__init__(
            row=True,
            align_center=True,
            class_="pa-5 ma-2",
            children=[v.Flex(xs12=True, children=[self.out])],
            **kwargs
        )

    def update_content(self, mkd_str):
        mkd = markdown(mkd_str, extensions=['fenced_code','sane_lists', 'mdx_math'])
        with self.out:
            self.out.clear_output()
            ipydisplay.display(ipydisplay.HTML(mkd))

        # self.content.template = f'<div>{mkd}</div>'