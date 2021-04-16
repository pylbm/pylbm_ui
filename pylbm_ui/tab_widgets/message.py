import ipyvuetify as v

class Message(v.Container):
    def __init__(self, message):
        self.message = v.Alert(children=[f'{message}...'], class_='primary--text')

        super().__init__(children=[
            v.Row(children=[
                v.ProgressCircular(indeterminate=True, color='primary', size=70, width=4)
                ], justify='center'),
            v.Row(children=[
                self.message,
                ], justify='center')
        ])

    def update(self, new_message):
        self.message.children = [f'{message}...']