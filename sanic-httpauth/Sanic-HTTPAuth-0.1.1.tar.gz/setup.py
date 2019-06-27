"""
Sanic-HTTPAuth
--------------

Basic and Digest HTTP authentication for Sanic routes.
"""
import re
from setuptools import setup

with open("sanic_httpauth.py", "r") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="Sanic-HTTPAuth",
    version=version,
    url="http://github.com/MihaiBalint/sanic-httpauth/",
    license="MIT",
    author="Mihai Balint",
    author_email="balint.mihai@gmail.com",
    description="Basic, Digest and Bearer token authentication for Sanic routes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["sanic_httpauth", "sanic_httpauth_compat"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=["sanic"],
    extras_require={
        "session": ["sanic_session"],
        "test": ["sanic_session", "sanic-cors", "ipdb"],
    },
    test_suite="tests",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
