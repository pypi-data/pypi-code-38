import setuptools
from distutils.core import Extension
from Cython.Build import cythonize
import numpy,os

with open("README.md", "r") as fh:
    long_description = fh.read()

# module extension
ext = Extension("bfit.fitting.integrator",
                sources=["./bfit/fitting/integrator.pyx",
                        "./bfit/fitting/FastNumericalIntegration_src/integration_fns.cpp"],
                language="c++",             # generate C++ code                        
                include_dirs=["./bfit/fitting/FastNumericalIntegration_src",numpy.get_include()],
                libraries=["m"],
                extra_compile_args=['-std=c++11',"-ffast-math"]
                )

setuptools.setup(
    name="bfit",
    version="2.2.0",
    author="Derek Fujimoto",
    author_email="fujimoto@phas.ubc.ca",
    description="BNMR/BNQR Data Fitting and Visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dfujim/bfit",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ),
    install_requires=['cython>=0.28','numpy>=1.14','tqdm>=4.31'
                      'bdata>=2.0.0','matplotlib>=2.2.2','pandas>=0.23.0'],
    package_data={'': ['./images/']},
    include_package_data=True,
    ext_modules = cythonize([ext],include_path = [numpy.get_include()]),
)
