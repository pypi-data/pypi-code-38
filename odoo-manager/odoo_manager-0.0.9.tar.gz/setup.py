import setuptools
import odoo_manager
from setuptools import Command, find_packages, setup
from subprocess import call


with open("readme.md", "r") as fh:
    long_description = fh.read()


class RunTests(Command):
    description = "run tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = call(["py.test"])
        raise SystemExit(errno)


setuptools.setup(
    name="odoo_manager",
    version=odoo_manager.version,
    author="Blue Stingray",
    author_email="odoo@bluestingray.com",
    description="Odoo manager utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["docopt==0.6.2", "invoke==1.1.*", "configparser==3.7.3", "black==19.3b0"],
    packages=setuptools.find_packages(exclude=["docs", "tests*"]),
    python_requires=">=3.3",
    entry_points={"console_scripts": ["odoo-manager=odoo_manager.cli.cli:main"]},
    extras_require={"test": ["coverage", "pytest", "pytest-cov"]},
    cmdclass={"test": RunTests},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)
