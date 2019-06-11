from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
      package_data = { 'PD': ['pd_data.txt'], 'Example': ['example_data.txt']},
      install_requires=['scipy', 'numpy', 'pandas', 'graphviz', 'Cython', 'portmin'],
      name="semopy",
      version="1.2.0",
      author="Meshcheryakov A. Georgy",
      author_email="metsheryakov_ga@spbstu.ru",
      description="Structural Equation Modeling optimization package.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://bitbucket.org/herrberg/semopy/",
      packages=find_packages(),
      classifiers=[
              "Programming Language :: Python :: 3",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent"])
