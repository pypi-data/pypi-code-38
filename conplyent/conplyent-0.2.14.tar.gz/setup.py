from setuptools import setup


setup(
    name="conplyent",
    version="0.2.14",
    license="MIT",
    author="Jayesh Joshi",
    author_email="jayeshjo1@utexas.edu",
    url="https://github.com/joshijayesh/conplyent/",
    description="Local and Remote Console executor",
    packages=["conplyent", "conplyent_scripts"],
    install_requires=[
        "pyzmq==17.1.2",
        "click>=7.0",
        "psutil>=5.4.5"],
    entry_points={
        "console_scripts": [
            "conplyent=conplyent_scripts.cli:cli"
        ],
    },
    python_requires=">=3.4.3",
)
