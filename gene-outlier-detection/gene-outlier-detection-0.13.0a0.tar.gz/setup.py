# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gene_outlier_detection']

package_data = \
{'': ['*']}

install_requires = \
['arviz>=0.4.0,<0.5.0',
 'click>=7.0,<8.0',
 'matplotlib>=3.0,<4.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.24.1,<0.25.0',
 'pymc3>=3.6,<4.0',
 'scipy>=1.2,<2.0',
 'seaborn>=0.9.0,<0.10.0',
 'sklearn>=0.0.0,<0.0.1',
 'tables>=3.5,<4.0',
 'theano>=1.0.4,<2.0.0',
 'tqdm>=4.31,<5.0']

entry_points = \
{'console_scripts': ['outlier-detection = '
                     'gene_outlier_detection.meta_runner:cli']}

setup_kwargs = {
    'name': 'gene-outlier-detection',
    'version': '0.13.0a0',
    'description': 'A Bayesian model for identifying gene expression outliers for individual single samples (N-of-1) when compared to a cohort of background datasets.',
    'long_description': None,
    'author': 'John Vivian',
    'author_email': 'jtvivian@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
