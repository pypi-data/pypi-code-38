import setuptools

setuptools.setup(
    name='maracatu',
    version="1.0.12",
    author="Diego Pinheiro",
    author_email="diegompin@gmail.com",
    description="Maracatu is a plotting package",
    url="https://github.com/diegompin/maracatu",
    packages=setuptools.find_packages(),
    license='',
    install_requires=[
          'pandas', 'matplotlib', 'numpy'
      ],
)
