# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mlxtk',
 'mlxtk.inout',
 'mlxtk.plot',
 'mlxtk.scripts',
 'mlxtk.systems',
 'mlxtk.systems.single_species',
 'mlxtk.tasks',
 'mlxtk.templates',
 'mlxtk.tools',
 'mlxtk.ui']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'doit==0.31.1',
 'future>=0.17.1,<0.18.0',
 'h5py>=2.9.0,<3.0.0',
 'jinja2>=2.10.1,<3.0.0',
 'matplotlib>=3.1.0,<4.0.0',
 'numba>=0.43.1,<0.45.0',
 'numpy-stl>=2.10.0,<3.0.0',
 'numpy==1.16.4',
 'pandas>=0.24.2,<0.25.0',
 'pathos>=0.2.3,<0.3.0',
 'pyside2>=5.12.3,<6.0.0',
 'pyyaml>=5.1,<6.0',
 'scipy>=1.3.0,<2.0.0',
 'sympy>=1.4,<2.0',
 'tabulate>=0.8.3,<0.9.0',
 'tqdm>=4.32.1,<5.0.0']

entry_points = \
{'console_scripts': ['dmat2_slider = mlxtk.scripts.dmat2_slider:main',
                     'dmat_evec_slider = mlxtk.scripts.dmat_evec_slider:main',
                     'fixed_ns = mlxtk.scripts.fixed_ns:main',
                     'fixed_ns_table = mlxtk.scripts.fixed_ns_table:main',
                     'gpop_model = mlxtk.scripts.gpop_model:main',
                     'gpop_slider = mlxtk.scripts.gpop_slider:main',
                     'mlxtkenv = mlxtkenv_script:main',
                     'plot_energy = mlxtk.scripts.plot_energy:main',
                     'plot_energy_diff = mlxtk.scripts.plot_energy_diff:main',
                     'plot_entropy = mlxtk.scripts.plot_entropy:main',
                     'plot_entropy_diff = mlxtk.scripts.plot_entropy_diff:main',
                     'plot_expval = mlxtk.scripts.plot_expval:main',
                     'plot_gpop = mlxtk.scripts.plot_gpop:main',
                     'plot_natpop = mlxtk.scripts.plot_natpop:main',
                     'plot_natpop_vs_dmat_evals = '
                     'mlxtk.scripts.plot_natpop_vs_dmat_evals:main',
                     'plot_spfs = mlxtk.scripts.plot_spfs:main',
                     'scan_plot_depletion = '
                     'mlxtk.scripts.scan_plot_depletion:main',
                     'scan_plot_energy = mlxtk.scripts.scan_plot_energy:main',
                     'scan_plot_expval = mlxtk.scripts.scan_plot_expval:main',
                     'scan_plot_gpop = mlxtk.scripts.scan_plot_gpop:main',
                     'scan_plot_natpop = mlxtk.scripts.scan_plot_natpop:main',
                     'spectrum_1b = mlxtk.scripts.spectrum_1b:main',
                     'thin_out_psi = mlxtk.scripts.thin_out_psi:main']}

setup_kwargs = {
    'name': 'mlxtk',
    'version': '0.5.3',
    'description': 'Toolkit to design, run and analyze ML-MCTDH(X) simulations',
    'long_description': 'mlxtk\n=====\nToolkit to design, run and analyze ML-MCTDH(X) simulations\n\nDescription\n-----------\nmlxtk gives the user a simple interface to setup physical systems and provides\ncommon simulation tasks to be used as building blocks to set up rather complex\nsimulations. Data is automatically stored in efficient formats (i.e. HDF5 and\ngzipped files).\n\nSimulations can also be used in the context of parameter scans where each\nsimulation is executed for each specified parameter combination. Submission\nof simulation jobs to computing clusters is easily achieved from the command\nline.\n\nFurthermore, analysis and plotting tools are provided to interpret the\nsimulation outcome.\n',
    'author': 'Fabian Köhler',
    'author_email': 'fkoehler@physnet.uni-hamburg.de',
    'url': 'https://github.com/f-koehler/mlxtk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
