# Install to Python 3
# python3 setup.py sdist bdist_wheel  # <--------- This may not be necessary unless I plan to upload the package to PyPI
# python3 -m pip install --user --editable ./
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="examsage",
    version="0.0.1.dev2",
    author="Michael Barnard",
    author_email="mbarnard10@ivytech.edu",
    description="ExamSage is a Python package for generating math problems in $LaTeX$. The goal of this project is to allow math instructors to create randomizable math problems and assessments without extensive programming knowledge.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/examsage/",
    packages=[
        'examsage',
    ],
    scripts=[
        'bin/makeproblem.py',
        'bin/newproblem.py',
    ],
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)