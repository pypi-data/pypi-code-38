import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ComboFinder",
    version="0.1.1",
    author="Prabhdeep Singh",
    author_email="singh_prabhdeep@outlook.in",
    description="Groups products into combos such that the cummulative price is attractive.",
    py_modules = ["ComboFinder"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WWFelina/ComboFinder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)