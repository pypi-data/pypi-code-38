# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hilde',
 'hilde.fireworks',
 'hilde.fireworks.scripts',
 'hilde.fireworks.workflows',
 'hilde.harmonic_analysis',
 'hilde.helpers',
 'hilde.helpers.sobol',
 'hilde.helpers.supercell',
 'hilde.k_grid',
 'hilde.konstanten',
 'hilde.materials_fp',
 'hilde.molecular_dynamics',
 'hilde.phono3py',
 'hilde.phonon_db',
 'hilde.phonopy',
 'hilde.relaxation',
 'hilde.scripts',
 'hilde.spglib',
 'hilde.structure',
 'hilde.tasks',
 'hilde.tasks.fireworks',
 'hilde.tasks.fireworks.fw_out',
 'hilde.tdep',
 'hilde.templates',
 'hilde.templates.lammps']

package_data = \
{'': ['*'],
 'hilde': ['WIP/*', 'WIP/statistical_sampling/*'],
 'hilde.scripts': ['run/*']}

install_requires = \
['ase>=3.17,<4.0',
 'matplotlib>=3.1,<4.0',
 'numpy>=1.16,<2.0',
 'phonopy>=2.1,<3.0',
 'scipy>=1.3,<2.0',
 'son>=0.1.4,<0.2.0',
 'spglib>=1.12,<2.0']

entry_points = \
{'console_scripts': ['make_supercell = hilde.scripts.make_supercell:main']}

setup_kwargs = {
    'name': 'hilde',
    'version': '0.2.1.dev1',
    'description': 'Haber Institute Lattice Dynamics Environment',
    'long_description': '**Installation**\n\nExternal dependencies:\n\n```\napt-get install gfortran liblapack-dev liblapacke-dev mongodb\n```\n\nInstall the python requirements in `requirements.txt` _in order_:\n\n```\ncat requirements.txt | xargs -n 1 -L 1 pip install --user\n```\n\nConfigure Hilde by creating a `~/.hilderc` configuration file in the home directory:\n\n```\ncp hilde/location/hilderc.template ~/.hilderc\n```\n\nand edit according to system. The `aims_command` is a command or script that takes care\nof running aims. This can be either just `mpirun aims.x`, or a script loading necessary\nmodules etc. and finally calling `srun aims.x` on a cluster.\n\nInstall Hilde:\n\n```\npip install --user -U .\n```\n\nAlternatively, you can create and activate a virtual environment holding the\nHilde installation and all dependencies like this:\n\n```\npython3 -m venv venv\nsource venv/bin/activate\ncat requirements.txt | xargs -n 1 -L 1 pip install\npip install .\n```\n\n**Settings Files**\n\n`hilde` uses the Python `configparser` module for parsing settings files named\n`settings.in` and the configuration file `hilde.cfg`. The\nparser is augmented by `JSON` so it understands any input on the right hand side that is\nvalid `JSON`. The inputs get converted to Python objects according to [this conversion\ntable](https://realpython.com/python-json/#serializing-json).\n\n**New Features**\n* Simplified Settings Files:\n  * Settings files named `settings.in` are automatically parsed when calling\n    `Settings()` within Hilde.\n  * The configuration file `hilde.cfg` gets installed to system.\n* Molecular dynamics workflow with input and output files\n  * see hilde/examples/md\n* Phonopy workflow with input and output files\n  * see hilde/examples/phonopy\n* Relaxation workflow with config file and output files\n  * see hilde/examples/relaxation\n* YAML Trajectories:\n  * save MD trajectories as YAML with tools in `hilde.trajectories`\n  * example in `hilde/examples/trajectory/trajectory.son.ipynb`\n* Emails:\n  * send notifications via email with `hilde.helpers.notifications.send_simple_mail`\n* Watchdogs:\n  * supervise e.g. an MD to estimate when the walltime will be reached.\n    Example in `examples/md/md_with_watchdog.ipynb`\n* Wrapper for `phono3py`\n  * Preprocess and re-creation of Phono3py objects from precomputed force\n  constants, see examples\n* Wrapper for `phonopy`\n  * Preprocess and (some) postprocess, see examples\n* Templates\n  * `from hilde.templates.lammps import setup_lammps_si` to provide lammps calculator\n* Brillouin zone helpers\n  * `hilde.helpers.brillouinzone` features `get_paths`, `get_bands`, and\n  `get_labels` to provide paths in the BZ that can be fed to `phonopy` via\n  `phonon.set_bandstructure(bands)`, and\n  `phonon.plot_band_structure(labels=labels)`.\n  * These functions are used by `hilde.phonopy.plot_dos_and_bandstructure` to\n  plot DOS and bandstructure in the working directory.\n* Scripts:\n  * `make_supercell`: create supercell from supercell matrix or\n  target target\n  * `geometry_info`: print geometry information for given input\n  structure\n* Symmetry Block Generation Functions\n  * `AtomsInput`: A storage class that stores relevant information about a structure\n  * `write_sym_constraints_geo`: Read any geometry.in file and use the list of `AtomInputs`\n  to create a new supercell with a user defined symmetry block added to it\n* FireWorks integration\n  * Functions that can be used with PyTask to use FireWorks as a job manager\n  * Jobs can now be submitted to the queue from a local machine and have the results processed locally\n\n\n**Setup of FireWorks on Computational Resources**\n\nSee also: `doc/README_FHI_FireWorksConnections.md`\n* Overview of Managing FireWorks Remotely\n  * FireWorks does not copy functions but only finds them in the PYTHONPATH\n  * To pass it functions give it the function_module.function_name as a str\n  * Functions that are run on the local machine\n    * All functions/files that set up FireWorks\n      * All scripts that initially call hilde.tasks.fireworks.generate_firework\n      * .cfg Files that define the steps (if used)\n      * All functions used by a Fireworks without a task that calls a function in task2queue list\n    * claunch_hilde and associated functions\n  * Function that are run on the remote machine\n    * All functions used by a Firework with a task that calls a function in task2queue\n    * qluanch_hilde and associated functions\n  * Functions that can run on both machines\n    * All FireWorks API functions\n    * All database accessors functions\n    * Spec modifying functions (hilde.tasks.fireworks.fw_action_outs)\n    * hilde.tasks.fireworks.generate_firework\n  * Machine specific settings such as the aims_command is handled dynamically\n    * It automatically changes when called on a machine\n    * Can always use local settings without an issue\n* Prerequisites for using FireWorks\n  * Fabric 2 (for remote connections)\n  * paramiko (used by Fabric 2)\n  * python-gssapi (for gss authorization)\n  * pymongo\n* Using FireWorks on the clusters\n  * Download/clone from https://github.com/materialsproject/fireworks.git and move the FireWorks directory\n  * Modify fw\\_tutorials/worker/my\\_fworker.yaml and copy it to $HOME/.fireworks\n    * Probably do not need to do any modifications if running on similar environments\n    * Useful if you want to run specific jobs on specific machines without specified reservations\n  * Modify fw\\_tutorials/worker/my\\_launchpad.yaml and copy it to $HOME/.fireworks\n    * host: Host to the DB server\n      * If connected through an ssh tunnel use localhost\n    * port: Port the DB server is listening on\n      * If connected through an ssh tunnel use the port connected the DB server via the tunnel\n    * username: username used to access the database\n    * password: password used to access the database\n    * logdir: default directory to store logs\n    * strm_lvl: How much information the launchpad prints by default\n  * Modify the correct fw\\_tutorials/queue\\_???.yaml file for your submission system and copy it to $HOME/.fireworks/my\\_qadapter.yaml\n    * Only used on clusters\n    * Set to minimal queue defaults\n      * nodes = 1\n      * ntasks_per_node = 32\n      * walltime = "00:30:00"\n      * queue = "express"\n      * logdir = /some/path/that/must/exist (make sure this exists)\n  * Find the FireWorks install directory with lpad version and modify\n    $FW_INSTALL_DIR/fireworks/fw_config.py:\n    * LAUNCHPAD_LOC: $HOME/.fireworks/my_launchpad.yaml\n    * FWORKER_LOC: $HOME/.fireworks/my_fworker.yaml\n    * QUEUEADAPTER_LOC: $HOME/.fireworks/my_qadapter.yaml\n* Setup a MongoDB database for fireworks\n  * Best to have it always accessible by all machines that need it\n  * Check with the cluster management on what solution they\'d prefer\n* Connections between computers\n  * Passwordless connections are preferred\n  * If this is not possible you can pass the password as a command line argument, (delete\n    bash history afterwards)\n* FireWorks Etiquette\n  * Name all Fireworks/WorkFlows\n  * If you are using a shared launchpad only use lpad reset if everyone is okay with that\n',
    'author': 'Florian Knoop',
    'author_email': 'knoop@fhi-berlin.mpg.de',
    'url': 'https://github.com/flokno/hilde',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
