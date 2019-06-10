# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cmlkit',
 'cmlkit.dataset',
 'cmlkit.engine',
 'cmlkit.evaluation',
 'cmlkit.evaluation.loss',
 'cmlkit.regression',
 'cmlkit.regression.qmml',
 'cmlkit.representation',
 'cmlkit.representation.mbtr',
 'cmlkit.representation.sf',
 'cmlkit.representation.soap',
 'cmlkit.tune',
 'cmlkit.tune.evaluators',
 'cmlkit.tune.run',
 'cmlkit.tune.search',
 'cmlkit.utility']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'ase>=3.17,<4.0',
 'dill>=0.2,<0.3',
 'hyperopt>=0.1.2,<0.2.0',
 'joblib>=0.13,<0.14',
 'numpy>=1.16,<2.0',
 'pebble>=4.3,<5.0',
 'son>=0.1.3,<0.2.0']

setup_kwargs = {
    'name': 'cmlkit',
    'version': '2.0.0a8',
    'description': 'Machine learning tools for computational chemistry and condensed matter physics',
    'long_description': '# cmlkit\n\n*"a kit for camels"* \n\n🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰🐫🧰\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cmlkit.svg) [![PyPI](https://img.shields.io/pypi/v/cmlkit.svg)](https://pypi.org/project/cmlkit/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n\n`cmlkit` provides a clean and concise way to specify, tune, and evaluate machine learning models for computational chemistry and condensed matter physics, particularly for atomistic predictions.\n\nWARNINGS: \n- `cmlkit` depends on [`qmmlpack`](https://gitlab.com/qmml/qmmlpack), which is *not* yet publicly available.\n- This is a "scientific code", i.e. development occurs infrequently and somewhat haphazardly. I\'ll try to not make breaking changes too often, and never in minor versions.\n- This is very domain-specific project, so it is somewhat full of jargon. The `tune` and `engine` sub-modules are quite general, though!\n\nIf you use this code in any scientific work, please mention it in the publication and let me know. Thanks! 🐫\n\n## What is `cmlkit`? 🐫🧰\n\nAt its core, `cmlkit` defines a unified `dict`-based format to specify model components, which can be straightforwardly read and written as `yaml`. It provides interfaces to implementations of popular methods in its domain using this format. Model components are implemented as pure-ish functions, which is conceptually satisfying and opens the door to easy pipelining and caching.\n\nOn this basis, it then implements parallel hyperparameter optimisation (using `hyperopt` as backend), and provides tools to train models, make predictions, and evaluate those predictions. It is intended to be extensible and flexible enough for the demands of research. It is also "high-performance computing compatible", i.e. it can run in computing environments straight from the 90s. 🤓\n\nOut of necessity, it also implements yet another dataset format, but makes up for it by providing automatic loading, which is neat.\n\n### Compatibility\n\nAt the moment, there are interfaces for:\n\nRepresentations:\n- Many-Body Tensor Representation (MBTR) (Huo, Rupp, arXiv 1704.06439 (2017)) (`qmmlpack` interface)\n- Smooth Overlap of Atomic Positions (SOAP) representaton (Bartok, Kondor, Csanyi, PRB 87, 184115 (2013)) (`quippy` interface)\n- Symmetry Functions (SF) representation (Behler, JCP 134, 074106 (2011)) (`RuNNer` interface)\n\nRegression methods:\n- Kernel Ridge Regression (KRR) as implemented in [`qmmlpack`](https://gitlab.com/qmml/qmmlpack)\n\n### Features\n\n- Reasonably clean, composable, modern codebase with little magic ✨\n\nThe hyperparameter optimisation (`cmlkit.tune`) boasts:\n- Robust multi-core support (i.e. it can automatically kill timed out external code, even if it ignores `SIGTERM`)\n- No `mongodb` required (important for *cough* certain computing environments *cough*)\n- Extensions to the `hyperopt` spaces (`log` grids)\n- Possibility to implement multi-step optimisation (experimental at the moment)\n- Resumable/recoverable runs backed by a readable, atomically written history of the optimisation (backed by [`son`](https://github.com/flokno/son))\n- Search spaces can be defined entirely in text, i.e. they\'re easily writeable, portable and serialisable\n\nOn the roadmap, coming soon™:\n- Thorough caching for computations (everything is prepared!)\n- Plugin system (currently, custom objects need to be registered manually)\n\n## Frequently Asked Questions\n\n(They are not actually frequently asked.)\n\n### I don\'t work in computational chemsitry/condensed matter physics. Should I care?\n\nThe short answer is regrettably probably no. \n\nHowever, I think the architecture of this library is quite neat, so maybe it can provide some marginally interesting reading. The `tune` component is very general and provides, in my opinion, a delightfully clean interface to `hyperopt`. The `engine` is also rather general and provides a somewhat nice way to serialise specific kinds of python objects to `yaml`.\n\n### Why should I use this?\n\nIf you need to use any of the libraries mentioned above it might be more convenient. If you need to do hyperparameter optimisation and are tired of plain `hyperopt` it might be useful.\n',
    'author': 'Marcel Langer',
    'author_email': 'dev@sirmarcel.com',
    'url': 'https://github.com/sirmarcel/cmlkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
