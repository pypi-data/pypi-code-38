import os
import codecs
import sys
from shutil import rmtree
from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))


with open("README.md", "r") as fh:
    long_description = fh.read()


# class PyTest(TestCommand):
#     user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

#     def initialize_options(self):
#         TestCommand.initialize_options(self)
#         self.pytest_args = ""

#     def run_tests(self):
#         import shlex

#         # import here, cause outside the eggs aren't loaded
#         import pytest

#         errno = pytest.main(shlex.split(self.pytest_args))
#         sys.exit(errno)




class UploadCommand(Command):
    """Support setup.py publish."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds...")
            rmtree(os.path.join(here, "dist"))
        except FileNotFoundError:
            pass
        self.status("Building Source distribution...")
        os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))
        self.status("Uploading the package to PyPi via Twine...")
        os.system("sudo twine upload dist/*")
        sys.exit()



setup(
    name="spaceman",
    version="0.2.3",
    author="Kevin Hill",
    author_email="kevin@funguana.com",
    description="Abstracted storage library. Allows for looking backwards dynamically and allows for quick custom storage to Amazaon S3",
    
    # long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["spaceman"],
    install_requires=['cloudpickle', 'funtime',
                      'coolname', "arctic_latest", "boto3", "s3fs", "loguru"],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        "pytest"
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={"upload": UploadCommand}
    # entry_points='''
    #     [console_scripts]
    #     decision=fundecision.manager:cli
    # '''   
)
