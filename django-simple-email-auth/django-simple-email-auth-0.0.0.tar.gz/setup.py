from setuptools import setup, find_packages


def get_description():
    with open("README.rst") as f:
        return f.read()


setup(
    # Package meta-data
    name="django-simple-email-auth",
    version="0.0.0",
    description="Django app for email based authentication and registration.",
    long_description=get_description(),
    author="Chathan Driehuys",
    author_email="chathan@driehuys.com",
    url="https://github.com/cdriehuys/django-simple-email-auth",
    license="MIT",
    # Additional classifiers for PyPI
    classifiers=[
        "Development Status :: 3 - Alpha",
        # Supported versions of Django
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        # Supported versions of Python
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # Include the actual source code
    include_package_data=True,
    packages=find_packages(),
    # Dependencies
    install_requires=["Django >= 1.10"],
)
