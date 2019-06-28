# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['foreshadow',
 'foreshadow.estimators',
 'foreshadow.intents',
 'foreshadow.tests',
 'foreshadow.tests.test_estimators',
 'foreshadow.tests.test_intents',
 'foreshadow.tests.test_transformers',
 'foreshadow.transformers.internals']

package_data = \
{'': ['*'],
 'foreshadow': ['optimizers/*', 'transformers/*'],
 'foreshadow.tests': ['test_configs/*', 'test_data/*']}

install_requires = \
['TPOT>=0.10.1,<0.11.0',
 'category-encoders>=1.2.8,<2.0.0',
 'fancyimpute>=0.3.2,<0.4.0',
 'numpy>=1.16.4,<2.0.0',
 'pandas>=0.23.3,<0.24.0',
 'scikit-learn>=0.19.2,<0.20.0',
 'scipy>=1.1.0,<2.0.0',
 'toml>=0.10.0,<0.11.0']

extras_require = \
{'dev': ['auto-sklearn==0.5.2']}

entry_points = \
{'console_scripts': ['foreshadow = foreshadow.console:cmd']}

setup_kwargs = {
    'name': 'foreshadow',
    'version': '0.1.0',
    'description': 'Peer into the future of a data science project',
    'long_description': "Foreshadow: Simple Machine Learning Scaffolding\n===============================================\n\n|BuildStatus| |DocStatus| |Coverage| |CodeStyle| |License|\n\nForeshadow is an automatic pipeline generation tool that makes creating, iterating,\nand evaluating machine learning pipelines a fast and intuitive experience allowing\ndata scientists to spend more time on data science and less time on code.\n\n.. |BuildStatus| image:: https://dev.azure.com/georgianpartners/foreshadow/_apis/build/status/georgianpartners.foreshadow?branchName=master\n   :target: https://dev.azure.com/georgianpartners/foreshadow/_build/latest?definitionId=1&branchName=master\n\n.. |DocStatus| image:: https://readthedocs.org/projects/foreshadow/badge/?version=latest\n  :target: https://foreshadow.readthedocs.io/en/latest/?badge=latest\n  :alt: Documentation Status\n\n.. |Coverage| image:: https://coveralls.io/repos/github/georgianpartners/foreshadow/badge.svg?branch=development\n  :target: https://coveralls.io/github/georgianpartners/foreshadow\n  :alt: Coverage\n\n.. |CodeStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n  :target: https://github.com/ambv/black\n  :alt: Code Style\n\n.. |License| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg\n  :target: https://github.com/georgianpartners/foreshadow/blob/master/LICENSE\n  :alt: License\n\nInstalling Foreshadow\n---------------------\n\n.. code-block:: console\n\n    $ pip install foreshadow\n\nRead the documentation to `set up the project from source`_.\n\n.. _set up the project from source: https://foreshadow.readthedocs.io/en/development/developers.html#setting-up-the-project-from-source\n\nGetting Started\n---------------\n\nTo get started with foreshadow, install the package using pip install. This will also\ninstall the dependencies. Now create a simple python script that uses all the\ndefaults with Foreshadow.\n\nFirst import foreshadow\n\n.. code-block:: python\n\n    import foreshadow as fs\n\nAlso import sklearn, pandas, and numpy for the demo\n\n.. code-block:: python\n\n    import pandas as pd\n\n    from sklearn.datasets import boston_housing\n    from sklearn.model_selection import train_test_split\n\nNow load in the boston housing dataset from sklearn into pandas dataframes. This\nis a common dataset for testing machine learning models and comes built in to\nscikit-learn.\n\n.. code-block:: python\n\n    boston = load_boston()\n    bostonX_df = pd.DataFrame(boston.data, columns=boston.feature_names)\n    bostony_df = pd.DataFrame(boston.target, columns=['target'])\n\nNext, exactly as if working with an sklearn estimator, perform a train test\nsplit on the data and pass the train data into the fit function of a new Foreshadow\nobject\n\n.. code-block:: python\n\n    X_train, X_test, y_train, y_test = train_test_split(bostonX_df,\n       bostony_df, test_size=0.2)\n    shadow = fs.Foreshadow()\n    shadow.fit(X_train, y_train)\n\nNow `fs` is a fit Foreshadow object for which all feature engineering has been\nperformed and the estimator has been trained and optimized. It is now possible to\nutilize this exactly as a fit sklearn estimator to make predictions.\n\n.. code-block:: python\n\n    shadow.score(X_test, y_test)\n\nGreat, you now have a working Foreshaow installation! Keep reading to learn how to\nexport, modify and construct pipelines of your own.\n\nKey Features\n------------\n- Automatic Feature Engineering\n- Automatic Model Selection\n- Rapid Pipeline Development / Iteration\n- Automatic Parameter Optimization\n- Ease of Extensibility\n- Scikit-Learn Compatible\n\nForeshadow supports python 3.6+\n\nDocumentation\n-------------\n`Read the docs!`_\n\n.. _Read the docs!: https://foreshadow.readthedocs.io/en/development/index.html\n",
    'author': 'Adithya Balaji',
    'author_email': 'adithyabsk@gmail.com',
    'url': 'https://foreshadow.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
