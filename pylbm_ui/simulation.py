import os
import json
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import pylbm

class Plot:
    def __init__(self, figsize=(10, 5)):
        plt.ioff()
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.canvas.header_visible = False
        self.plot_type = None
        self.color_bar = None

    def plot(self, t, domain, field, data):
        self.ax.title.set_text(f"time: {t} s")

        if domain.dim == 1:
            x = domain.x
            if self.plot_type is None:
                self.plot_type = self.ax.scatter(x, data, color='cadetblue', s=1)
            else:
                self.plot_type.set_offsets(np.c_[x, data])
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
                self.plot_type = self.ax.imshow(data.T, origin='lower')
                self.color_bar = self.fig.colorbar(self.plot_type, ax=self.ax)
            else:
                self.plot_type.set_array(data.T)
                self.plot_type.set_clim(vmin=np.nanmin(data), vmax=np.nanmax(data))
            self.color_bar.set_label(label=field)

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

    def reset_sol(self, test_case, lb_scheme, dx, codegen=None, codegen_dir=None, exclude=None, initialize=True):
        self.test_case = test_case
        self.lb_scheme = lb_scheme
        self.dx = dx
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

        if exclude:
            keys = list(simu_cfg['parameters'].keys())
            str_keys = [str(k) for k in simu_cfg['parameters'].keys()]
            for ik, k in enumerate(exclude):
                if isinstance(k, tuple):
                    for kk in k:
                        if kk in str_keys:
                            simu_cfg['parameters'].pop(keys[str_keys.index(kk)])
                else:
                    if k in str_keys:
                        simu_cfg['parameters'].pop(keys[str_keys.index(k)])

        self.simu_cfg = simu_cfg
        self.sol = pylbm.Simulation(simu_cfg, initialize=initialize)

    @property
    def duration(self):
        return self.test_case.duration

    def get_data(self, field):
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

        data[solid_cells[tuple(ind)]] = np.NaN
        return data

    def save_data(self, field):
        h5 = pylbm.H5File(self.sol.domain.mpi_topo, f'{field}', self.path, self.sol.nt)
        if self.sol.dim == 1:
            h5.set_grid(self.sol.domain.x)
        elif self.sol.dim == 2:
            h5.set_grid(self.sol.domain.x, self.sol.domain.y)
        data = self.get_data(field)
        h5.add_scalar(field, data)
        h5.save()

    def plot(self, fig, field):
        data = self.get_data(field)
        fig.plot(self.sol.t, self.sol.domain, field, data)

    def save_config(self, filename='simu_config.json'):
        json.dump(
            {
                'test_case': {
                    'module': self.test_case.__module__,
                    'class': self.test_case.__class__.__name__,
                    'args': json.loads(self.test_case.json(skip_defaults=True)),
                },
                'lb_scheme': {
                    'module': self.lb_scheme.__module__,
                    'class': self.lb_scheme.__class__.__name__,
                    'args': json.loads(self.lb_scheme.json(skip_defaults=True)),
                },
            },
            open(os.path.join(self.path, filename), 'w'),
            sort_keys=True,
            indent=4,
        )