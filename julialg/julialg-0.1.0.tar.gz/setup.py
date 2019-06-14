"""Setup file
"""


import setuptools
import julialg


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(name='julialg',
                 version=julialg.__version__,
                 description='Julia-style arrays in Python',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url=julialg.__github_url__,
                 author='James W. Kennington',
                 author_email='jameswkennington@gmail.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 zip_safe=False)
