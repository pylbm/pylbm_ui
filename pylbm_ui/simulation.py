# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import os
import json

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib
import copy
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pylbm

class Plot:
    def __init__(self):
        plt.ioff()
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.header_visible = False
        self.plot_type = None
        self.color_bar = None
        # plt.ion()

    def plot(self, t, domain, field, data, transpose=True, properties=None):
        from .config import plot_config
        properties = properties or {}
        if domain.dim == 1:
            x = domain.x
            if self.plot_type is None:
                label = f'{field}'
                color = plot_config['colors'][0]
                alpha = plot_config['alpha']
                linewidth = plot_config['linewidth']
                linestyle = plot_config['linestyle']
                marker = plot_config['marker']
                markersize = plot_config['markersize']
                if 'label' in properties:
                    label = properties['label']
                if 'color' in properties:
                    color = properties['color']
                if 'alpha' in properties:
                    alpha = properties['alpha']
                if 'linewidth' in properties:
                    linewidth = properties['linewidth']
                if 'linestyle' in properties:
                    linestyle = properties['linestyle']
                if 'marker' in properties:
                    marker = properties['marker']
                if 'markersize' in properties:
                    markersize = properties['markersize']

                self.plot_type, = self.ax.plot(
                    x, data,
                    label=label,
                    color=color,
                    alpha=alpha,
                    linewidth=linewidth,
                    linestyle=linestyle,
                    marker=marker,
                    markersize=markersize
                )
            else:
                self.plot_type.set_ydata(data)

            self.ax.relim()
            self.ax.autoscale_view()

            if not properties:
                self.ax.set_xlabel('x')
                self.ax.set_ylabel(field)

        elif domain.dim == 2:
            if self.plot_type is None:
                cmap = plot_config['cmap']
                if 'cmap' in properties:
                    cmap = plt.colormaps()[int(properties['cmap'])]
                cmap = copy.copy(matplotlib.cm.get_cmap(cmap))
                cmap.set_bad(plot_config['nan_color'], plot_config['alpha'])
                x, y = domain.x, domain.y
                extent = [np.amin(x), np.amax(x), np.amin(y), np.amax(y)]
                if transpose:
                    to_plot = data.T
                else:
                    to_plot = data

                self.plot_type = self.ax.imshow(to_plot, origin='lower',
                                                cmap=cmap, extent=extent,
                                                interpolation='bilinear')
                divider = make_axes_locatable(self.ax)
                cax = divider.append_axes("bottom", size="5%", pad=0.55)
                self.color_bar = self.fig.colorbar(
                    self.plot_type, cax=cax, orientation="horizontal"
                )
            else:
                self.plot_type.set_array(data.T)
            if 'min_value' in properties:
                vmin = properties['min_value']
            else:
                vmin = np.nanmin(data)

            if 'max_value' in properties:
                vmax = properties['max_value']
            else:
                vmax = np.nanmax(data)
            self.plot_type.set_clim(vmin=vmin, vmax=vmax)
            label = properties['label'] if 'label' in properties else field
            self.color_bar.set_label(label=label)

        if not properties:
            self.ax.title.set_text(f"time: {t} s")  #, fontsize=18)


def get_config(
    test_case, lb_scheme, dx,
    codegen=None, codegen_dir=None, exclude=None, show_code=False
):
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
            self.func[k] = sp.lambdify(
                list(v.atoms(sp.Symbol)), v, "numpy", dummify=False
            )

    def reset_sol(
        self,
        v_model,
        test_case, lb_scheme,
        dx,
        codegen=None, codegen_dir=None,
        exclude=None, initialize=True,
        show_code=False
    ):
        self.v_model = v_model
        self.test_case = test_case
        self.lb_scheme = lb_scheme
        self.dx = dx
        self.simu_cfg = get_config(
            test_case, lb_scheme,
            dx,
            codegen, codegen_dir, exclude, show_code
        )
        self.sol = pylbm.Simulation(
            self.simu_cfg, initialize=initialize
        )

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
        has_ref = hasattr(self.test_case, 'ref_solution')

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
                if has_ref:
                    data_ref = self.test_case.ref_solution(self.sol.t, self.sol.domain.x, f)
                    h5.add_scalar(f'{f}_ref', data_ref)
        else:
            data = self.get_data(field)
            h5.add_scalar(field, data)
            if has_ref:
                data_ref = self.test_case.ref_solution(self.sol.t, self.sol.domain.x, field)
                h5.add_scalar(f'{field}_ref', data_ref)

        h5.save()

    def plot(self, fig, field):
        data = self.get_data(field)
        fig.plot(self.sol.t, self.sol.domain, field, data)

    def save_config(self, filename='simu_config.json'):
        from .json import save_simu_config
        save_simu_config(self.path, filename, self.dx, self.v_model, self.test_case, self.lb_scheme)

    def save_stats(self, stats, filename='simu_config.json'):
        from .json import save_stats
        if self.path:
            save_stats(self.path, filename, stats)
