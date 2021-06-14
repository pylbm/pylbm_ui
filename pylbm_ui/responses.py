# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib
import copy
import pylbm
import re

relax_regexp = re.compile('s_(.*)')

class FromConfig:
    pass

class DuringSimulation:
    pass

class AfterSimulation:
    pass

class Sigma(FromConfig):
    def __init__(self, s, log10=False):
        self.log10 = log10
        self.s = s
        self.symb = relax_regexp.search(str(self.s)).group(1)

    def __call__(self, config, extra_config=None):
        extra_config = extra_config or {}
        params = config['parameters']
        params.update(extra_config)

        output = 1./params[self.s] - 0.5
        return np.log10(output) if self.log10 else output

    def __str__(self):
        out = ''
        if self.log10:
            out += 'Log'
        return out + f'Sig_{self.symb}'

class S(FromConfig):
    def __init__(self, s):
        self.s = s

    def __call__(self, config, extra_config=None):
        extra_config = extra_config or {}
        params = config['parameters']
        params.update(extra_config)

        output = params[self.s]
        return output

    def __str__(self):
        return f'{self.s}'

class Diff(FromConfig):
    def __init__(self, s, with_dx=True, log10=False):
        self.log10 = log10
        self.with_dx = with_dx
        self.s = s
        self.symb = relax_regexp.search(str(self.s)).group(1)

    def __call__(self, config, extra_config=None):
        extra_config = extra_config or {}
        params = config['parameters']
        params.update(extra_config)

        la = config['scheme_velocity']
        if isinstance(la, sp.Symbol):
            la = params[la]

        dx = config['space_step'] if self.with_dx else 1

        output = (1./params[self.s] - 0.5)*dx*la
        return np.log10(output) if self.log10 else output

    def __str__(self):
        out = ''
        if self.log10:
            out += 'Log'
        out += 'Diff'
        if self.with_dx:
            out += 'Odx'
        return out + f'_{self.symb}'

class LinearStability(FromConfig):
    def __init__(self, states):
        self.states = states

    def __call__(self, config, extra_config=None):
        scheme = pylbm.Scheme(config)
        stab = pylbm.Stability(scheme)
        n_wv = 1024

        for state in self.states:
            consm0 = [0.] * len(stab.consm)
            for k, moment in enumerate(stab.consm):
                consm0[k] = state.get(moment, 0.)

            stab.eigenvalues(consm0, n_wv, extra_config)

            if not stab.is_stable_l2:
                return False
        return True

    def __str__(self):
        return 'LinStab'

class Stability(FromConfig):
    def __init__(self, expr, tol=1e10):
        self.expr = expr
        self.tol = tol
        self.func = None
        self.nite = 0
        self.call_at = None
        self.is_stable = True
        self.solid_index = None

    def __call__(self, duration, sol):
        if self.call_at is None:
            self.call_at = int(duration/sol.dt/10)

        if self.func is None:
            func = sp.lambdify(list(self.expr.atoms(sp.Symbol)), self.expr, "numpy", dummify=False)
        to_subs = {str(k): sol.m[k] for k in sol.scheme.consm.keys()}
        to_subs.update({str(k): v for k, v in sol.scheme.param.items()})

        args = {str(s): to_subs[str(s)] for s in self.expr.atoms(sp.Symbol)}
        data = func(**args)

        # remove element with NaN values
        if self.solid_index is None:
            solid_cells = sol.domain.in_or_out != sol.domain.valin

            vmax = sol.domain.stencil.vmax
            ind = []
            for vm in vmax:
                ind.append(slice(vm, -vm))
            ind = np.asarray(ind)

            self.solid_index = solid_cells[tuple(ind)]

        if nite == self.call_at:
            data[self.solid_index] = 0

            if np.isnan(np.sum(data)) or np.any(np.abs(data)>self.tol):
                self.is_stable = False

        return self.is_stable

    def value(self):
        return self.is_stable

    def __str__(self):
        return 'Stab'

class Error(DuringSimulation):
    def __init__(self, ref_solution, expr, log10=True, relative=False):
        self.func = None
        self.ref_solution = ref_solution
        self.expr = expr
        self.log10 = log10
        self.relative = relative
        self.solid_index = None

    def __call__(self, sol):
        if self.func is None:
            func = sp.lambdify(list(self.expr.atoms(sp.Symbol)), self.expr, "numpy", dummify=False)
        to_subs = {str(k): sol.m[k] for k in sol.scheme.consm.keys()}
        to_subs.update({str(k): v for k, v in sol.scheme.param.items()})

        args = {str(s): to_subs[str(s)] for s in self.expr.atoms(sp.Symbol)}
        data = func(**args)

        # remove element with NaN values
        if self.solid_index is None:
            solid_cells = sol.domain.in_or_out != sol.domain.valin

            vmax = sol.domain.stencil.vmax
            ind = []
            for vm in vmax:
                ind.append(slice(vm, -vm))
            ind = np.asarray(ind)

            self.solid_index = solid_cells[tuple(ind)]

        data[self.solid_index] = 0

        norm = np.linalg.norm(self.ref_solution - data)
        if self.relative:
            norm /= np.linalg.norm(self.ref_solution)
        return np.log10(norm) if self.log10 else norm

    def __str__(self):
        return 'Error'
class ErrorStd(DuringSimulation):
    def __init__(self, field, ref_func, expr, call_at=0.92, log10=True):
        self.field = field
        self.ref_func = ref_func
        self.expr = expr
        self.log10 = log10
        self.error = []
        self.call_at = call_at
        self.error_func = None

    def __call__(self, duration, sol):
        start_time = self.call_at*duration

        if sol.t >= start_time:
            domain = sol.domain
            ref_solution = self.ref_func(sol.t, domain.x, field=self.field)

            if self.error_func is None:
                self.error_func = Error(ref_solution, self.expr, log10=False, relative=False)
            else:
                self.error_func.ref_solution = ref_solution

            self.error.append(self.error_func(sol))

        return True

    def value(self):
        std = np.std(np.asarray(self.error))
        return np.log10(std) if self.log10 else std

    def __str__(self):
        return f'ErrStd_{self.field}'

class ErrorAvg(ErrorStd):
    def value(self):
        avg = np.average(np.asarray(self.error))
        return np.log10(avg) if self.log10 else avg

    def __str__(self):
        return f'ErrAvg_{self.field}'

class CFL(AfterSimulation):
    def __init__(self, rho, q):
        self.rho = rho
        self.q = q

    def __call__(self, sol):
        output = 0
        for q in self.q:
            data = sol.m[q]/sol.m[self.rho]
            output += np.amax(data)

        la = sol.scheme.la
        if isinstance(la, sp.Symbol):
            if la in sol.scheme.param:
                la = sol.scheme.param[la]
            elif la in sol.extra_parameters:
                la = sol.extra_parameters[la]
            else:
                raise KeyError(f'{la} not found')

        return output/la

    def __str__(self):
        return 'CFL'

class Plot(AfterSimulation):
    def __init__(self, filename, expr, ref_solution=None):
        self.filename = filename
        self.expr = expr
        self.ref_solution = ref_solution

    def __call__(self, sol):
        func = sp.lambdify(list(self.expr.atoms(sp.Symbol)), self.expr, "numpy", dummify=False)
        to_subs = {str(k): sol.m[k] for k in sol.scheme.consm.keys()}
        to_subs.update({str(k): v for k, v in sol.scheme.param.items()})

        args = {str(s): to_subs[str(s)] for s in self.expr.atoms(sp.Symbol)}
        data = func(**args)

        solid_cells = sol.domain.in_or_out != sol.domain.valin

        vmax = sol.domain.stencil.vmax
        ind = []
        for vm in vmax:
            ind.append(slice(vm, -vm))
        ind = np.asarray(ind)

        data[solid_cells[tuple(ind)]] = np.nan

        fig, ax = plt.subplots()
        if sol.dim == 1:
            x = sol.domain.x
            ax.plot(x, data,
                    color='black',
                    alpha=0.8,
                    linewidth=2,
                    marker='.',
                    markersize=10,
                    )
            if self.ref_solution is not None:
                ax.plot(x, self.ref_solution,
                    color='black',
                    alpha=0.8,
                    linewidth=1,
                    )
        elif sol.dim == 2:
            x, y = sol.domain.x, sol.domain.y
            cmap = copy.copy(matplotlib.cm.get_cmap("RdBu"))
            cmap.set_bad('black', 0.8)
            extent = [np.amin(x), np.amax(x), np.amin(y), np.amax(y)]
            imshow = ax.imshow(data.T, origin='lower', cmap=cmap, extent=extent)
            fig.colorbar(imshow, ax=ax)

        fig.savefig(self.filename, dpi=300)
