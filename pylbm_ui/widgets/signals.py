# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

from traitlets import UseEnum, HasTraits, observe
import enum

class SignalType(enum.Enum):
    simulation = 1
    green = 2
    blue = 3
    yellow = 4

class Signal(HasTraits):
    type = UseEnum(SignalType, allow_none=True).tag(sync=True)

    def emit(self, signal_type):
        self.type = signal_type
        signal.notify_change({'name': 'type', 'type': 'change'})

signal = Signal()