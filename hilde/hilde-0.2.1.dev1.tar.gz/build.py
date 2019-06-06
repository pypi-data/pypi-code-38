"""provide numpy extension to compile fortran routines"""
from numpy.distutils.core import setup, Extension

ext = Extension(
    name="hilde.helpers.supercell.supercell",
    sources=[
        "hilde/helpers/supercell/linalg.f90",
        "hilde/helpers/supercell/supercell.f90",
    ],
    extra_compile_args=["-O3"],
)


def build(setup_kwargs):
    """add Extension to setup kwargs"""

    setup_kwargs.update({"ext_modules": [ext]})
