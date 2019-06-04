import sys
import os
from setuptools import setup, find_packages

__version__ = "2019.1.3"

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

# 'setup.py test' shortcut.
# !pip install --index-url https://test.pypi.org/simple/ sensiml -U
if sys.argv[-1] == 'test':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')
    sys.exit()

setup(
    name='SensiML',
    description='SensiML Analytic Suite Python client',
    version=__version__,
    author='SensiML',
    author_email='support@sensiml.com',
    license='Proprietary',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['*test*', ]),
    package_data={
        'sensiml.datasets': ['*.csv'],
        'sensiml.widgets': ['*.pem'],
        'sensiml.image': ['*.png'],
    },
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[
        'cookiejar',
        'requests>=2.14.2',
        'requests-oauthlib>=0.7.0',
        'appdirs>=1.4.3',
        'semantic_version>=2.6.0',
        'jupyter>=1.0.0',
        'numpy>=1.13',
        'pandas>=0.20.3',
        'matplotlib>=2.0.0',
        'nrfutil>=3.3.2,<=5.0.0',
        'qgrid>=1.0.2',
        'prompt-toolkit>=2.0.5; python_version>="3"',
        'prompt-toolkit<=1.0.4; python_version<"3"',
        'jupyter-console>=6.0.0; python_version>="3"',
        'notebook==5.7.5; python_version>="3"',
        'jupyter-console<=5.2.0; python_version<"3"',
        'ipython>=7.0.1; python_version>="3"',
        'ipython<=5.8.0; python_version<"3"',
        'bqplot',
        'seaborn',
        'wurlitzer',
        'jupyter-contrib-nbextensions',
        'pyserial',
    ],
)
