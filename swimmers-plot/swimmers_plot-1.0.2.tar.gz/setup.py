from setuptools import setup

setup(
    name='swimmers_plot',
    version='1.0.2',
    packages=['swimmers_plot'],
    install_requires=['numpy', 'matplotlib', 'intervaltree'],
    url='https://github.com/broadinstitute/swimmers_plot',
    license='MIT',
    author='Justin Cha',
    author_email='jcha@broadinstitute.org',
    description='Create a swimmer\'s plot of treatments for a cohort',
    long_description='''# swimmers_plot
Create a swimmer's plot of treatments for a cohort

To install:

`pip install swimmers-plot`

To use:

```
import swimmers_plot
cohort = swimmers_plot.Cohort()
cohort.load_samples('sample_inp.tsv')
cohort.load_treatments('treatment_inp.tsv')
cohort.make_swimmers_plot()
```
'''
)
