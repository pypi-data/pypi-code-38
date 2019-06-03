from os import path
from setuptools import setup, find_packages


PROJECT_DIR = path.abspath(path.dirname(__file__))


with open(path.join(PROJECT_DIR, "README.md")) as f:
    long_description = f.read()


setup(
    name="lint_django_migrations",
    version="1.0.6",
    description="Detect backward incompatible migrations for your django project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cedar-team/lint_django_migrations",
    author="Cedar",
    author_email="support@cedar.com",
    license="Apache License 2.0",
    packages=find_packages(exclude=["tests/"]),
    install_requires=["django>=1.11", "appdirs==1.4.3"],
    extras_require={"test": ["tox==3.9.0", "pyfakefs==3.5.8", "django_add_default_value==0.3.1", "psycopg2"]},
    keywords="django migration lint linter database backward compatibility",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
