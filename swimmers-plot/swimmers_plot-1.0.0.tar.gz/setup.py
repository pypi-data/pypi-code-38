from setuptools import setup

setup(
    name='swimmers_plot',
    version='1.0.0',
    packages=['swimmers_plot'],
    install_requires=['numpy', 'matplotlib', 'intervaltree'],
    url='https://github.com/broadinstitute/swimmers-plot',
    license='MIT',
    author='Justin Cha',
    author_email='jcha@broadinstitute.org',
    description='Create a swimmer\'s plot of treatments for a cohort'
)
