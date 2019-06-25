import os
from setuptools import setup

NAME = "inscribe"
HERE = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(HERE, NAME, '_version.py')) as f:
    exec(f.read(), {}, version_ns)

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

with open("inscribe/requirements.txt") as f:
    requirements = [line for line in f.readlines() if (line and "#" not in line and "--" not in line)]

setup(
    name=NAME,
    long_description=README,
    long_description_content_type="text/x-rst",
    url='https://docs.inscribe.ai',
    license='GPL',
    maintainer='inscribe.ai',
    maintainer_email='team@inscribe.ai',
    version=version_ns['__version__'],
    packages=("inscribe",),
    package_dir={'inscribe': 'inscribe'},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=requirements
)
