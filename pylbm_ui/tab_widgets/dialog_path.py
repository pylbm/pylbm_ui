import ipyvuetify as v
import os
import shutil

from .pylbmwidget import out

class DialogPath(v.Dialog):
    def __init__(self):
        with out:
            yes = v.Btn(children=['yes'], class_='ma-2', style_='width: 100px', color='success')
            no = v.Btn(children=['no'], class_='ma-2', style_='width: 100px', color='error')
            self.width = '500'
            self.v_model = False
            self.text = v.CardTitle(children=[])
            self.children = [
                        v.Card(children=[self.text,
                                         v.CardActions(children=[v.Spacer(), yes, no])
                    ]),
            ]

            self.path = None
            self.replace = True

            yes.on_event('click', self.yes_click)
            no.on_event('click', self.no_click)

            super().__init__()

    def check_path(self, path):
        if os.path.exists(path):
            if os.listdir(path):
                self.path = path
                self.text.children = [f'{path} is not empty. Do you want to replace the files?']
                self.v_model = True

    def yes_click(self, widget, event, data):
        try:
            shutil.rmtree(self.path)
        except OSError:
            # Could be some issues on Windows
            pass
        self.v_model = False
        self.replace = True

    def no_click(self, widget, event, data):
        self.replace = False
        self.v_model = False

