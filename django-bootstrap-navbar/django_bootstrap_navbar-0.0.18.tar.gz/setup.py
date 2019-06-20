from setuptools import setup, find_packages
from subprocess import Popen

import sys
import shutil


VERSION = "0.0.18"


if sys.argv[-1] == "publish":
    print("Publishing django-bootstrap-navbar")

    process = Popen(["python", "setup.py", "sdist"])
    process.wait()

    process = Popen(
        ["twine", "upload", f"dist/django_bootstrap_navbar-{VERSION}.tar.gz"]
    )
    process.wait()

    shutil.rmtree("dist")
    shutil.rmtree("django_bootstrap_navbar.egg-info")
    sys.exit()


if sys.argv[-1] == "test":
    print("Running tests only on current environment.")

    process = Popen(["black", "./bootstrap_navbar"])
    process.wait()

    process = Popen(["pytest", "--cov=bootstrap_navbar", "--cov-report=html"])
    process.wait()

    sys.exit()


with open("README.md") as f:
    readme = f.read()


setup(
    name="django_bootstrap_navbar",
    version="0.0.18",
    description="Django navbar package",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Bradley Stuart Kirton",
    author_email="bradleykirton@gmail.com",
    url="https://gitlab.com/BradleyKirton/django-bootstrap-navbar/",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["django"],
    extras_require={
        "dev": [
            "pytest",
            "pytest-mock",
            "pytest-cov",
            "pytest-sugar",
            "django-coverage-plugin",
            "pytest-django",
            "bumpversion",
            "black",
            "twine",
        ]
    },
    zip_safe=False,
    keywords="django",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.1",
    ],
)
