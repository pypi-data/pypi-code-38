
from setuptools import setup, find_packages

version = '2019.6.8'

setup(
    name='ordered_namespace',
    packages=find_packages(),
    install_requires=[],

    version=version,
    author='Pierre V. Villeneuve',
    author_email='pierre.villeneuve@gmail.com',
    description='An easy-to-use Python namespace class derived from OrderedDict, includes tab-completion',
    url='https://github.com/who8mylunch/OrderedNamespace',
    license='MIT',
    keywords=['namespace', 'ordereddict', 'structure', 'dotdict', 'tab-completion'],
)
