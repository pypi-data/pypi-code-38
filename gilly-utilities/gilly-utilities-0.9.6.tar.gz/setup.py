import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gilly-utilities",
    version="0.9.6",
    author="James Gilmore",
    author_email="jamesgillygilmore@gmail.com",
    description="A data analysis package built upon Numpy, SciPy and Pandas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pacificgilly1992/Gilly_Utilities",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'scipy!=1.3.0',
        'pandas',
        'matplotlib',
        'statsmodels',
        'scikit-learn',
        'scikits.bootstrap',
        'patsy'
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)