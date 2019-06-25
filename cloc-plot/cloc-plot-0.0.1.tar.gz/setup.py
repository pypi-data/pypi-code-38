import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloc-plot",
    version="0.0.1",
    author="Fin Christensen",
    author_email="christensen.fin@gmail.com",
    description="View the source code count of several project in a pie chart",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fin-ger/py-cloc-plot",
    packages=setuptools.find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [ 'cloc-plot = cloc_plot:main' ]
    }
)
