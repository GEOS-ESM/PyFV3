import pyFV3.stencils.moist_cv as moist_cv
from ndsl.dsl.stencil import StencilFactory
from ndsl.namelist import Namelist
from pyFV3.testing import TranslateDycoreFortranData2Py


class TranslateLastStep(TranslateDycoreFortranData2Py):
    def __init__(
        self,
        grid,
        namelist: Namelist,
        stencil_factory: StencilFactory,
    ):
        super().__init__(grid, namelist, stencil_factory)
        self.compute_func = stencil_factory.from_origin_domain(  # type: ignore
            moist_cv.moist_pt_last_step,
            origin=self.grid.compute_origin(),
            domain=self.grid.domain_shape_compute(add=(0, 0, 1)),
        )
        self.in_vars["data_vars"] = {
            "qvapor": {},
            "qliquid": {},
            "qice": {},
            "qrain": {},
            "qsnow": {},
            "qgraupel": {},
            "pt": {},
            "pkz": {"istart": grid.is_, "jstart": grid.js},
            "gz": {
                "serialname": "gz1d",
                "kstart": grid.is_,
                "axis": 0,
                "full_shape": True,
            },
        }
        self.in_vars["parameters"] = ["r_vir", "dtmp"]
        self.out_vars = {
            "gz": {
                "serialname": "gz1d",
                "istart": grid.is_,
                "iend": grid.ie,
                "jstart": grid.je,
                "jend": grid.je,
                "kstart": grid.npz - 1,
                "kend": grid.npz - 1,
            },
            "pt": {},
        }
        self.write_vars = ["gz"]
        self.stencil_factory = stencil_factory
