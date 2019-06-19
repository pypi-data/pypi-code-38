from setuptools import setup

from os import path
project_dir = path.abspath(path.dirname(__file__))
with open(path.join(project_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='burdock-lab',
    version='0.0.7a1',
    packages=['burdock_lab'],
    url='https://github.com/DylanLukes/burdock_lab',
    license='BSD 3-Clause',

    author='Dylan A. Lukes',
    author_email='dlukes@eng.ucsd.edu',
    description='JupyterLab integration for Burdock, a Daikon frontend for data frames.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=[],
    include_package_data=True
)
