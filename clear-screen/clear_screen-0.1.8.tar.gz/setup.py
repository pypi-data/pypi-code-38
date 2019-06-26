import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clear_screen",
    version="0.1.8",
    author="James Loye Colley",
    description="A simple class for clearing a Python Interpreter Shell",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rootVIII/clear_screen",
    install_requires=[],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
