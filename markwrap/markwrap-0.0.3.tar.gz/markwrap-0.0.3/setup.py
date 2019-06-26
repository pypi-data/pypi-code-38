import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="markwrap",
    version="0.0.3",
    author="Will Markley",
    author_email="willmarkley@protonmail.com",
    description="Python wrappers around common dependencies",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/willmarkley/markwrap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: System",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=[''],
)
