import os
import json

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib
import pylbm

from .config import plot_config
from .json import save_simu_config

class Plot:
    def __init__(self, figsize=(10, 5)):
        plt.ioff()
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.canvas.header_visible = False
        self.plot_type = None
        self.color_bar = None

    def plot(self, t, domain, field, data):
        self.ax.title.set_text(f"time: {t} s")#, fontsize=18)

        if domain.dim == 1:
            x = domain.x
            if self.plot_type is None:
                self.plot_type = self.ax.plot(x, data,
                                              color=plot_config['colors'][0],
                                              alpha=plot_config['alpha'],
                                              linewidth=plot_config['linewidth'],
                                              marker=plot_config['marker'],
                                              markersize=plot_config['markersize'])[0]
            else:
                self.plot_type.set_ydata(data)
            xmin, xmax = x[0], x[-1]
            ymin, ymax = np.amin(data), np.amax(data)
            xeps = 0.1*(xmax - xmin)
            yeps = 0.1*(ymax - ymin)
            self.ax.set_xlim(xmin - xeps, xmax + xeps)
            self.ax.set_ylim(ymin - yeps, ymax + yeps)
            self.ax.set_xlabel('x')
            self.ax.set_ylabel(field)
        elif domain.dim == 2:
            if self.plot_type is None:
                cmap = plot_config['cmap']
                cmap.set_bad(plot_config['nan_color'], plot_config['alpha'])
                x, y = domain.x, domain.y
                extent = [np.amin(x), np.amax(x), np.amin(y), np.amax(y)]
                self.plot_type = self.ax.imshow(data.T, origin='lower', cmap=cmap, extent=extent)
                self.color_bar = self.fig.colorbar(self.plot_type, ax=self.ax)
            else:
                self.plot_type.set_array(data.T)
            self.plot_type.set_clim(vmin=np.nanmin(data), vmax=np.nanmax(data))
            self.color_bar.set_label(label=field)

def get_config(test_case, lb_scheme, dx, codegen=None, codegen_dir=None, exclude=None, show_code=False):
    simu_cfg = test_case.get_dictionary()
    param = simu_cfg['parameters']
    simu_cfg.update(lb_scheme.get_dictionary())
    param.update(simu_cfg['parameters'])
    simu_cfg['parameters'] = param
    simu_cfg['space_step'] = dx

    if codegen in ['numpy', 'cython']:
        simu_cfg['generator'] = codegen
    if codegen_dir:
        simu_cfg['codegen_option'] = {'directory': codegen_dir}

    bound_cfg = {}
    bound_tc = test_case.get_boundary()
    bound_sc = lb_scheme.get_boundary()
    for key, val in bound_tc.items():
        bound_cfg[key] = bound_sc[val]

    simu_cfg.pop('dim')
    simu_cfg['boundary_conditions'] = bound_cfg

    simu_cfg['show_code'] = show_code

    if exclude:
        for ik, k in enumerate(exclude):
            if isinstance(k, tuple):
                for kk in k:
                    if kk in simu_cfg['parameters']:
                        simu_cfg['parameters'].pop(kk)
            else:
                if k in simu_cfg['parameters']:
                    simu_cfg['parameters'].pop(k)

    return simu_cfg
class simulation:
    def __init__(self):
        self.sol = None
        self.fields = None
        self.test_case = None
        self.lb_scheme = None
        self.path = None
        self.dx = None
        self.simu_cfg = None

    def reset_path(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self.path = path

    def reset_fields(self, fields):
        self.fields = fields
        self.func = {}
        for k, v in fields.items():
            self.func[k] = sp.lambdify(list(v.atoms(sp.Symbol)), v, "numpy", dummify=False)

    def reset_sol(self, test_case, lb_scheme, dx, codegen=None, codegen_dir=None, exclude=None, initialize=True, show_code=False):
        self.test_case = test_case
        self.lb_scheme = lb_scheme
        self.dx = dx
        self.simu_cfg = get_config(test_case, lb_scheme, dx, codegen, codegen_dir, exclude, show_code)
        self.sol = pylbm.Simulation(self.simu_cfg, initialize=initialize)

    @property
    def duration(self):
        return self.test_case.duration

    def get_data(self, field, solid_value=np.NaN):
        to_subs = {str(k): self.sol.m[k] for k in self.sol.scheme.consm.keys()}
        to_subs.update({str(k): v for k, v in self.sol.scheme.param.items()})

        args = {str(s): to_subs[str(s)] for s in self.fields[field].atoms(sp.Symbol)}
        data = self.func[field](**args)
        # remove element with NaN values
        solid_cells = self.sol.domain.in_or_out != self.sol.domain.valin

        vmax = self.sol.domain.stencil.vmax
        ind = []
        for vm in vmax:
            ind.append(slice(vm, -vm))
        ind = np.asarray(ind)

        data[solid_cells[tuple(ind)]] = solid_value
        return data

    def save_data(self, field):
        if isinstance(field, set):
            filename = 'solution'
        else:
            filename = f'{field}'

        h5 = pylbm.H5File(self.sol.domain.mpi_topo, filename, self.path, self.sol.nt)

        if self.sol.dim == 1:
            h5.set_grid(self.sol.domain.x)
        elif self.sol.dim == 2:
            h5.set_grid(self.sol.domain.x, self.sol.domain.y)

        if isinstance(field, set):
            for f in field:
                data = self.get_data(f)
                h5.add_scalar(f, data)
        else:
            data = self.get_data(field)
            h5.add_scalar(field, data)

        h5.save()

    def plot(self, fig, field):
        data = self.get_data(field)
        fig.plot(self.sol.t, self.sol.domain, field, data)

    def save_config(self, filename='simu_config.json'):
        save_simu_cfg(self.path, filename, self.dx, self.test_case, self.lb_scheme)
