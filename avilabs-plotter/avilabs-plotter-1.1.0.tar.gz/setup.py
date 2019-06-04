from setuptools import setup, find_packages


long_description = '''
# Plotter
A sane plotting and charting API with pluggable backends.

# Quickstart
```python
import plotter as pltr
pltr.set_backend(pltr.MatplotlibBackend)

nodes = ['master', 'worker1', 'worker2']
cpus = [0.1, 0.6, 0.4]
cpusbar = pltr.VerticalBar(categories=nodes, values=cpus)
pltr.show_plot('CPU Performance', cpusbar)
```

For more details see the [Homepage](https://gitlab.com/avilay/plotter)
'''


setup(
    name='avilabs-plotter',
    version='1.1.0',
    description='Python plotting APIs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Avilay Parekh',
    author_email='avilay@gmail.com',
    license='MIT',
    url='https://gitlab.com/avilay/plotter',
    packages=find_packages(),
    install_requires=['matplotlib', 'numpy'],
)
