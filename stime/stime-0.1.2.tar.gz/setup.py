import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stime",
    version="0.1.2",
    author="Gonzalo Bulnes Guilpain",
    author_email="gon.bulnes@fastmail.com",
    description="A testing (and partial) replacement for the time package, for fully-controlled time-dependent tests.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gonzalo-bulnes/stime",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
