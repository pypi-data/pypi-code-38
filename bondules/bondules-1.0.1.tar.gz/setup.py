import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bondules',
    packages=['bondules'],
    description='Utility code created and used by Bon Crowder',
    version='1.0.1',
    url='http://github.com/mathfour/bondules',
    author='Bon Crowder @MathFour',
    author_email='bon@mathfour.com',
    keywords=['pip','mathfour','utility', 'Bon Crowder'],
    # packages=setuptools.find_packages(),
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ]
    )