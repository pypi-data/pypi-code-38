import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="predictiveopt",
    version="0.0.1",
    author="Dobromir Marinov",
    author_email="mr.d.marinov@gmail.com",
    description="Package containing an implementation of the Predictive Hyperparameter Optimisation algorithm.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DobromirM/Predictive-Hyperparameter-Optimisation",
    packages=setuptools.find_packages(exclude=['test']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
