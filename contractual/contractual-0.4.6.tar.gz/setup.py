from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="contractual",
    use_scm_version=True,
    description="Contractual provides a method for verifying the function of mocks across modules and projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/pjbecotte/contractual",
    author="Paul Becotte",
    author_email="pjbecotte@gmail.com",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="contract test pact verify",
    packages=find_packages(exclude=["docs", "tests"]),
    python_requires=">=3.7, <4",
    setup_requires=["setuptools_scm", "wheel"],
    install_requires=[],
)
