import setuptools
from distutils.dir_util import remove_tree

setuptools.setup(
    name="pyratfun",
    version="0.1.1",
    author="Mario Gely",
    author_email="mario.f.gely@gmail.com",
    description="Rational Function manipulation in python",
    long_description='Rational Function manipulations in python (and some extensions to the NumPy Polynomial class)',
    long_description_content_type="text/markdown",
    url="https://github.com/mgely/PyRatFun",
    package_dir={'pyratfun': 'src'},
    packages= ['pyratfun'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.0.0',
    include_package_data=False,
)