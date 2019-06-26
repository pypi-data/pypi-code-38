import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README")) as fd:
    README = fd.read()


setup(
    name="happinesspacket_schema",
    version="1.0.0",
    description="A schema package for Fedora Happiness Packets",
    long_description=README,
    url="https://pagure.io/fedora-commops/fedora-happiness-packets",
    # Possible options are at https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    license="GPLv2+",
    maintainer="Fedora Infrastructure Team",
    maintainer_email="infrastructure@lists.fedoraproject.org",
    platforms=["Fedora", "GNU/Linux"],
    keywords="fedora",
    packages=find_packages(exclude=("happinesspacket_schema.tests", "happinesspacket_schema.tests.*")),
    include_package_data=True,
    zip_safe=False,
    install_requires=["fedora_messaging"],
    test_suite="happinesspacket_schema.tests",
    entry_points={
        "fedora.messages": [
            "happinesspacket.messageV1=happinesspacket_schema.schema:MessageV1",
        ]
    },
)
