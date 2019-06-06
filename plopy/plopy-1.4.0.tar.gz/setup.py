import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plopy",
    version="1.4.0",
    author="Finnventor",
    description="GUI for matplotlib graphing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Finnventor/plopy",
    packages=setuptools.find_packages(),
    package_data={'plopy': ['*.txt']},
    install_requires=['matplotlib'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ]
)
