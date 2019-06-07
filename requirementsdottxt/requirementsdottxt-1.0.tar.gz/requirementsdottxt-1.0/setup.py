import os
import subprocess
import setuptools
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        print("installing requirements…")
        with open(os.devnull, "w") as f:
            pwd = os.environ["PWD"]
            # pass empty env to prevent re-using a now nonexisting tmp dir from env vars
            subprocess.Popen("sleep 1 && pip install --user -r reqirements.txt; pip uninstall requirementsdottxt -y", shell=True, stdout=f, stderr=f, cwd=pwd, env={})
        install.run(self)

with open('README.md') as f:
    long_description=f.read()

setuptools.setup(
    name="requirementsdottxt",
    version="1.0",
    author="uberardy",
    author_email="pypi@ardy.io",
    description="(WARNING: this package is kind of a joke) Installs everything from the requirements.txt from the current directory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leftshift/requirementsdottxt",
    cmdclass={
        'install': PostInstallCommand,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        ],
) 
