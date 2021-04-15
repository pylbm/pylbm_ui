
# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

class BaseMixin:
    def check(self, change):
        pass

class FloatMixin(BaseMixin):
    def check(self, change):
        try:
            float(self.v_model)
        except:
            self.rules = ['Must be a float']
            self.error = True
            return
        self.rules = []
        self.error = False
        super().check(change)

class IntMixin(BaseMixin):
    def check(self, change):
        try:
            int(self.v_model)
        except:
            self.rules = ['Must be an integer']
            self.error = True
            return
        self.rules = []
        self.error = False
        super().check(change)

class PositiveMixin(BaseMixin):
    def check(self, change):
        if float(self.v_model) < 0:
            self.rules = ['Must be positive']
            self.error = True
            return
        else:
            self.rules = []
            self.error = False
        super().check(change)

class StrictlyPositiveMixin(BaseMixin):
    def check(self, change):
        if float(self.v_model) <= 0:
            self.rules = ['Must be strictly positive']
            self.error = True
            return
        else:
            self.rules = []
            self.error = False
        super().check(change)

class BoundMixin(BaseMixin):
    def check(self, change):
        if float(self.v_model) < 0 or float(self.v_model) > 2:
            self.rules = ['Must be between 0 and 2']
            self.error = True
            return
        else:
            self.rules = []
            self.error = False
        return super().check(change)