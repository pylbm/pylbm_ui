# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import ipyvuetify as v
import traitlets

from .pylbmwidget import out

class add_rule:
    def __init__(self, method):
        self.method = method

    @staticmethod
    def __call__(self, *args, **kwargs):
        result = self.method(self, *args, **kwargs)
        return result

class MetaFormBase(type):
    def __new__(self, name, bases, namespace):
        rules = []
        for k, v in namespace.items():
            if isinstance(v, add_rule):
                namespace[k] = v.method
                rules.append(v.method)
        namespace['rules'] = rules
        return super().__new__(self, name, bases, namespace)

class MetaForm(MetaFormBase, traitlets.traitlets.MetaHasTraits):
    pass

class Form(v.Form, metaclass=MetaForm):
    def check_rules(self):
        self.v_model = True
        for r in self.rules:
            r(self, None)

        for f in self.fields:
            if hasattr(f, 'error'):
                if f.error:
                    self.v_model = False
                    break

    def check_changes(self, change):
        self.check_rules()

    def reset_form(self):
        for f in self.fields:
            if not isinstance(f, v.TextField):
                if isinstance(f, v.Select) and f.multiple:
                    f.v_model = []
                else:
                    f.v_model = None
            f.rules = []
            f.error = False

        self.v_model = False

class Item(v.ListItem):
    form_class = None
    update_text = ''

    def __init__(self, *args, **kwargs):
        self.form = self.form_class(*args, **kwargs)

        update_btn = v.Btn(children=['update'], color='success')
        close_btn = v.Btn(children=['close'], color='error')

        self.update_dialog = v.Dialog(
            width='500',
            v_model=False,
            children=[
                v.Card(children=[
                    v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                        self.update_text
                    ]),
                    v.CardText(children=[self.form]),
                    v.CardActions(children=[v.Spacer(), update_btn, close_btn])
            ]),
        ])

        update_btn.on_event('click', self.update_click)
        close_btn.on_event('click', self.close_click)

        self.content = v.CardText(children=[f'{self}'])

        self.btn = v.Btn(children=[v.Icon(children=['mdi-close'])],
                         fab=True,
                         color='error',
                         dark=True,
                         x_small=True,
        )

        super().__init__(children=[
            v.ListItemAction(children=[self.btn]),
            v.ListItemContent(
                children=[
                    v.Card(children=[self.content],
                           flat=True,
                           color='transparent',
                           light=True,
                    ),
                self.update_dialog
                ]),
            ], **kwargs)

    def close_click(self, widget, event, data):
        self.update_dialog.v_model = False

    def update_click(self, widget, event, data):
        self.form.check_rules()

        if self.form.v_model:
            self.form2field()
            self.content.children = [f'{self}']
            self.update_dialog.v_model = False

        self.notify_change({'name': 'children', 'type': 'change'})

    def update_item(self, widget, event, data):
        self.form.reset_form()
        self.field2form()
        self.update_dialog.v_model = True

class Dialog:
    item_class = None
    new_text = ''

    def __init__(self, *args, **kwargs):
        with out:
            self.form = self.item_class.form_class(*args, **kwargs)

            create_add = v.Btn(children=['add'], color='success')
            create_close = v.Btn(children=['close'], color='error')

            create_dialog = v.Dialog(
                width='500',
                v_model=False,
                children=[
                    v.Card(children=[
                        v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                            self.new_text
                        ]),
                        v.CardText(children=[self.form]),
                        v.CardActions(children=[v.Spacer(), create_add, create_close])
                ]),
            ])

            self.item_list = v.List(children=[])
            add_button = v.Btn(children=[v.Icon(children=['mdi-plus']), create_dialog],
                            fab=True,
                            color='primary',
                            small=True,
                            dark=True,
            )

            def close_click(widget, event, data):
                create_dialog.v_model = False

            def on_change(change):
                self.item_list.notify_change({'name': 'children', 'type': 'change'})

            def add_click(widget, event, data):
                self.form.check_rules()

                if self.form.v_model:
                    new_item = self.create_item()
                    self.item_list.children.append(new_item)
                    create_dialog.v_model = False

                    def remove_item(widget, event, data):
                        self.item_list.children.remove(new_item)
                        self.item_list.notify_change({'name': 'children', 'type': 'change'})

                    new_item.btn.on_event('click', remove_item)
                    new_item.on_event('click', new_item.update_item)
                    new_item.observe(on_change, 'children')

                    self.item_list.notify_change({'name': 'children', 'type': 'change'})

            create_close.on_event('click', close_click)
            create_add.on_event('click', add_click)

            def on_add_click(widget, event, data):
                with out:
                    self.form.reset_form()
                    create_dialog.v_model = True

            add_button.on_event('click', on_add_click)

            self.add_button = add_button
            self.widget = v.Card(children=[
                v.CardText(children=[self.item_list]),
                v.CardActions(children=[v.Spacer(), add_button])
            ])

    def purge(self):
        self.item_list.children = []