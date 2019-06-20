#!/usr/bin/env python

# Setup script for PyPI; use CMakeFile.txt to build extension modules

from setuptools import setup
from distutils.command.install_headers import install_headers
from pybind11 import __version__
import os

# Prevent installation of pybind11 headers by setting
# PYBIND11_USE_CMAKE.
if os.environ.get('PYBIND11_USE_CMAKE'):
    headers = []
else:
    headers = [
        'include/pybind11/detail/class.h',
        'include/pybind11/detail/common.h',
        'include/pybind11/detail/descr.h',
        'include/pybind11/detail/init.h',
        'include/pybind11/detail/internals.h',
        'include/pybind11/detail/typeid.h',
        'include/pybind11/attr.h',
        'include/pybind11/buffer_info.h',
        'include/pybind11/cast.h',
        'include/pybind11/chrono.h',
        'include/pybind11/complex.h',
        'include/pybind11/eigen.h',
        'include/pybind11/embed.h',
        'include/pybind11/eval.h',
        'include/pybind11/functional.h',
        'include/pybind11/iostream.h',
        'include/pybind11/numpy.h',
        'include/pybind11/operators.h',
        'include/pybind11/options.h',
        'include/pybind11/pybind11.h',
        'include/pybind11/pytypes.h',
        'include/pybind11/stl.h',
        'include/pybind11/stl_bind.h',
		'include/pybind11/variables.h',
		'include/pybind11/instances.h',
		'include/pybind11/missing_values.h',
		'include/pybind11/data_set.h',
		'include/pybind11/inputs.h',
		'include/pybind11/outputs.h',
		'include/pybind11/unscaling_layer.h',
		'include/pybind11/scaling_layer.h',
		'include/pybind11/inputs_trending_layer.h',
		'include/pybind11/outputs_trending_layer.h',
		'include/pybind11/probabilistic_layer.h',
		'include/pybind11/perceptron_layer.h',
		'include/pybind11/neural_network.h',
		'include/pybind11/multilayer_perceptron.h',
		'include/pybind11/bounding_layer.h',
		'include/pybind11/sum_squared_error.h',
		'include/pybind11/loss_index.h',
		'include/pybind11/normalized_squared_error.h',
		'include/pybind11/minkowski_error.h',
		'include/pybind11/mean_squared_error.h',
		'include/pybind11/weighted_squared_error.h',
		'include/pybind11/cross_entropy_error.h',
		'include/pybind11/training_strategy.h',
		'include/pybind11/quasi_newton_method.h',
		'include/pybind11/stochastic_gradient_descent.h',
		'include/pybind11/levenberg_marquardt_algorithm.h',
		'include/pybind11/gradient_descent.h',
		'include/pybind11/conjugate_gradient.h',
		'include/pybind11/model_selection.h',
		'include/pybind11/order_selection_algorithm.h',
		'include/pybind11/incremental_order.h',
		'include/pybind11/golden_section_order.h',
		'include/pybind11/simulated_annealing_order.h',
		'include/pybind11/inputs_selection_algorithm.h',
		'include/pybind11/growing_inputs.h',
		'include/pybind11/pruning_inputs.h',
		'include/pybind11/genetic_algorithm.h',
		'include/pybind11/testing_analysis.h',
		'include/pybind11/numerical_integration.h',
		'include/pybind11/numerical_differentiation.h',
		'include/pybind11/principal_components_layer.h',
		'include/pybind11/selective_pruning.h',
		'include/pybind11/file_utilities.h',
		'include/pybind11/association_rules.h',
		'include/pybind11/text_analytics.h',
		'include/pybind11/tinyxml2.h',
		'include/pybind11/correlation_analysis.h',
		'include/pybind11/optimization_algorithm.h',
		'include/pybind11/learning_rate_algorithm.h',
		'include/pybind11/adaptive_moment_estimation.h'
		'include/pybind11/functions.h'
		'include/pybind11/layer.h'
		'include/pybind11/products.h'
		'include/pybind11/pooling_layer.h'
    ]


class InstallHeaders(install_headers):
    """Use custom header installer because the default one flattens subdirectories"""
    def run(self):
        if not self.distribution.headers:
            return

        for header in self.distribution.headers:
            subdir = os.path.dirname(os.path.relpath(header, 'include/pybind11'))
            install_dir = os.path.join(self.install_dir, subdir)
            self.mkpath(install_dir)

            (out, _) = self.copy_file(header, install_dir)
            self.outfiles.append(out)


setup(
    name='pybind11',
    version=__version__,
    description='Seamless operability between C++11 and Python',
    author='Wenzel Jakob',
    author_email='wenzel.jakob@epfl.ch',
    url='https://github.com/wjakob/pybind11',
    download_url='https://github.com/wjakob/pybind11/tarball/v' + __version__,
    packages=['pybind11'],
    license='BSD',
    headers=headers,
    cmdclass=dict(install_headers=InstallHeaders),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Programming Language :: C++',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License'
    ],
    keywords='C++11, Python bindings',
    long_description="""pybind11 is a lightweight header-only library that
exposes C++ types in Python and vice versa, mainly to create Python bindings of
existing C++ code. Its goals and syntax are similar to the excellent
Boost.Python by David Abrahams: to minimize boilerplate code in traditional
extension modules by inferring type information using compile-time
introspection.

The main issue with Boost.Python-and the reason for creating such a similar
project-is Boost. Boost is an enormously large and complex suite of utility
libraries that works with almost every C++ compiler in existence. This
compatibility has its cost: arcane template tricks and workarounds are
necessary to support the oldest and buggiest of compiler specimens. Now that
C++11-compatible compilers are widely available, this heavy machinery has
become an excessively large and unnecessary dependency.

Think of this library as a tiny self-contained version of Boost.Python with
everything stripped away that isn't relevant for binding generation. Without
comments, the core header files only require ~4K lines of code and depend on
Python (2.7 or 3.x, or PyPy2.7 >= 5.7) and the C++ standard library. This
compact implementation was possible thanks to some of the new C++11 language
features (specifically: tuples, lambda functions and variadic templates). Since
its creation, this library has grown beyond Boost.Python in many ways, leading
to dramatically simpler binding code in many common situations.""")
