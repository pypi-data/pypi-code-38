import setuptools

from pyberdrola import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_requirements():
    """
    Returns a list of dependencies from the `requirements.txt` file
    """
    dep = []

    with open("requirements.txt", "r") as fp:
        line = fp.readline()
        while line:
            dep.append(line.strip())
            line = fp.readline()

    return dep


setuptools.setup(
    name="pyberdrola",
    version=__version__,
    author="Jorge Maroto",
    author_email="patoroco@gmail.com",
    description="A client to use www.iberdrola.es from the terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/patoroco/pyberdrola",
    install_requires=get_requirements(),
    packages=setuptools.find_packages(),
    py_modules=["cli"],
    entry_points={"console_scripts": ["pyberdrola = cli:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
