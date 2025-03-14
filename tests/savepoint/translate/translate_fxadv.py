import numpy as np

from ndsl.constants import X_DIM, Y_DIM, Z_DIM
from ndsl.dsl.stencil import StencilFactory
from ndsl.namelist import Namelist
from pyFV3.stencils import FiniteVolumeFluxPrep
from pyFV3.testing import TranslateDycoreFortranData2Py
from pyFV3.utils.functional_validation import get_subset_func


class TranslateFxAdv(TranslateDycoreFortranData2Py):
    def __init__(
        self,
        grid,
        namelist: Namelist,
        stencil_factory: StencilFactory,
    ):
        super().__init__(grid, namelist, stencil_factory)
        utinfo = grid.x3d_domain_dict()
        utinfo["serialname"] = "ut"
        vtinfo = grid.y3d_domain_dict()
        vtinfo["serialname"] = "vt"
        self.stencil_factory = stencil_factory
        self.compute_func = FiniteVolumeFluxPrep(  # type: ignore
            self.stencil_factory,
            self.grid.grid_data,
            namelist.grid_type,
        )
        self.in_vars["data_vars"] = {
            "uc": {},
            "vc": {},
            "uc_contra": utinfo,
            "vc_contra": vtinfo,
            "x_area_flux": {
                **{"serialname": "xfx_adv"},
                **grid.x3d_compute_domain_y_dict(),
            },
            "crx": {**{"serialname": "crx_adv"}, **grid.x3d_compute_domain_y_dict()},
            "y_area_flux": {
                **{"serialname": "yfx_adv"},
                **grid.y3d_compute_domain_x_dict(),
            },
            "cry": {**{"serialname": "cry_adv"}, **grid.y3d_compute_domain_x_dict()},
        }
        self.in_vars["parameters"] = ["dt"]
        self.out_vars = {
            "uc_contra": utinfo,
            "vc_contra": vtinfo,
        }
        for var in ["x_area_flux", "crx", "y_area_flux", "cry"]:
            self.out_vars[var] = self.in_vars["data_vars"][var]

        self._subset = get_subset_func(
            self.grid.grid_indexing,
            dims=[X_DIM, Y_DIM, Z_DIM],
            n_halo=((2, 2), (2, 2)),
        )

    def subset_output(self, varname: str, output: np.ndarray) -> np.ndarray:
        """
        Given an output array, return the slice of the array which we'd
        like to validate against reference data
        """
        if varname in ["uc_contra", "vc_contra", "ut", "vt"]:
            return self._subset(output)
        else:
            return output

    def compute_from_storage(self, inputs):
        self.compute_func(**inputs)
        for name in ["uc_contra", "vc_contra"]:
            inputs[name] = self.subset_output(name, inputs[name])

        return inputs
