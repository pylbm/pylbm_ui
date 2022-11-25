# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause
import pylbm
import numpy as np
import sympy as sp

class SlipXEven(pylbm.bc.BoundaryMethod):
    """
    Slip boundary condition
    """
    def set_iload(self):
        """
        Compute the indices that are needed
        (symmertic velocities and space indices).
        """
        k = self.istore[0]
        ksym = self.stencil.get_symmetric(axis=0)[k]
        v = self.stencil.get_all_velocities()
        indices = self.istore[1:] -v[ksym].T
        self.iload.append(np.concatenate([ksym[np.newaxis, :], indices]))

    def set_rhs(self):
        """
        Compute and set the additional terms to fix the boundary values.
        """
        k = self.istore[:, 0]
        ksym = self.stencil.get_symmetric()[k]
        self.rhs[:] = self.feq[k, np.arange(k.size)] - \
            self.feq[ksym, np.arange(k.size)]

    # pylint: disable=too-many-locals
    def generate(self, sorder):
        """
        Generate the numerical code.

        Parameters
        ----------
        sorder : list
            the order of nv, nx, ny and nz
        """
        from pylbm.generator import For
        from pylbm.symbolic import nx, ny, nz, indexed, ix

        ns = int(self.stencil.nv_ptr[-1])
        dim = self.stencil.dim

        istore, iload, ncond = self._get_istore_iload_symb(dim)
        rhs, _ = self._get_rhs_dist_symb(ncond)

        idx = sp.Idx(ix, (0, ncond))
        fstore = indexed(
            'f', [ns, nx, ny, nz],
            index=[istore[idx, k] for k in range(dim+1)],
            priority=sorder
        )
        fload = indexed(
            'f', [ns, nx, ny, nz],
            index=[iload[0][idx, k] for k in range(dim+1)],
            priority=sorder
        )

        self.generator.add_routine(
            ('slip_xeven', For(idx, sp.Eq(fstore, fload + rhs[idx])))
        )

    @property
    def function(self):
        """Return the generated function"""
        return self.generator.module.slip_xeven


class SlipXOdd(pylbm.bc.BoundaryMethod):
    """
    Slip boundary condition
    """
    def set_iload(self):
        """
        Compute the indices that are needed
        (symmertic velocities and space indices).
        """
        k = self.istore[0]
        ksym = self.stencil.get_symmetric(axis=0)[k]
        v = self.stencil.get_all_velocities()
        indices = self.istore[1:] -v[ksym].T
        self.iload.append(np.concatenate([ksym[np.newaxis, :], indices]))

    def set_rhs(self):
        """
        Compute and set the additional terms to fix the boundary values.
        """
        k = self.istore[:, 0]
        ksym = self.stencil.get_symmetric()[k]
        self.rhs[:] = self.feq[k, np.arange(k.size)] - \
            self.feq[ksym, np.arange(k.size)]

    # pylint: disable=too-many-locals
    def generate(self, sorder):
        """
        Generate the numerical code.

        Parameters
        ----------
        sorder : list
            the order of nv, nx, ny and nz
        """
        from pylbm.generator import For
        from pylbm.symbolic import nx, ny, nz, indexed, ix

        ns = int(self.stencil.nv_ptr[-1])
        dim = self.stencil.dim

        istore, iload, ncond = self._get_istore_iload_symb(dim)
        rhs, _ = self._get_rhs_dist_symb(ncond)

        idx = sp.Idx(ix, (0, ncond))
        fstore = indexed(
            'f', [ns, nx, ny, nz],
            index=[istore[idx, k] for k in range(dim+1)],
            priority=sorder
        )
        fload = indexed(
            'f', [ns, nx, ny, nz],
            index=[iload[0][idx, k] for k in range(dim+1)],
            priority=sorder
        )

        self.generator.add_routine(
            ('slip_xodd', For(idx, sp.Eq(fstore, -fload + rhs[idx])))
        )

    @property
    def function(self):
        """Return the generated function"""
        return self.generator.module.slip_xodd


class SlipYEven(pylbm.bc.BoundaryMethod):
    """
    Slip boundary condition (Y-axis)
    """
    def set_iload(self):
        """
        Compute the indices that are needed
        (symmertic velocities and space indices).
        """
        k = self.istore[0]
        ksym = self.stencil.get_symmetric(axis=1)[k]
        v = self.stencil.get_all_velocities()

        # print(k, ksym, v[k], v[ksym])
        indices = self.istore[1:] -v[ksym].T
        self.iload.append(np.concatenate([ksym[np.newaxis, :], indices]))

    def set_rhs(self):
        """
        Compute and set the additional terms to fix the boundary values.
        """
        k = self.istore[:, 0]
        ksym = self.stencil.get_symmetric(axis=1)[k]
        self.rhs[:] = self.feq[k, np.arange(k.size)] - \
            self.feq[ksym, np.arange(k.size)]

    # pylint: disable=too-many-locals
    def generate(self, sorder):
        """
        Generate the numerical code.

        Parameters
        ----------
        sorder : list
            the order of nv, nx, ny and nz
        """
        from pylbm.generator import For
        from pylbm.symbolic import nx, ny, nz, indexed, ix

        ns = int(self.stencil.nv_ptr[-1])
        dim = self.stencil.dim

        istore, iload, ncond = self._get_istore_iload_symb(dim)
        rhs, _ = self._get_rhs_dist_symb(ncond)

        idx = sp.Idx(ix, (0, ncond))
        fstore = indexed(
            'f', [ns, nx, ny, nz],
            index=[istore[idx, k] for k in range(dim+1)],
            priority=sorder
        )
        fload = indexed(
            'f', [ns, nx, ny, nz],
            index=[iload[0][idx, k] for k in range(dim+1)],
            priority=sorder
        )

        self.generator.add_routine(
            ('slip_YEven', For(idx, sp.Eq(fstore, fload + rhs[idx])))
        )

    @property
    def function(self):
        """Return the generated function"""
        return self.generator.module.slip_YEven


class SlipYOdd(SlipYEven):

    """
    Slip boundary condition (Y-axis)
    """
    # pylint: disable=too-many-locals
    def generate(self, sorder):
        """
        Generate the numerical code.

        Parameters
        ----------
        sorder : list
            the order of nv, nx, ny and nz
        """
        from pylbm.generator import For
        from pylbm.symbolic import nx, ny, nz, indexed, ix

        ns = int(self.stencil.nv_ptr[-1])
        dim = self.stencil.dim

        istore, iload, ncond = self._get_istore_iload_symb(dim)
        rhs, _ = self._get_rhs_dist_symb(ncond)

        idx = sp.Idx(ix, (0, ncond))
        fstore = indexed(
            'f', [ns, nx, ny, nz],
            index=[istore[idx, k] for k in range(dim+1)],
            priority=sorder
        )
        fload = indexed(
            'f', [ns, nx, ny, nz],
            index=[iload[0][idx, k] for k in range(dim+1)],
            priority=sorder
        )

        self.generator.add_routine(
            ('slip_YOdd', For(idx, sp.Eq(fstore, -fload + rhs[idx])))
        )

    @property
    def function(self):
        """Return the generated function"""
        return self.generator.module.slip_YOdd
