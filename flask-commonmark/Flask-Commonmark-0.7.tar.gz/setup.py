"""
flask_commonmark
----------------

Add commonmark processing filter to your Flask app.

"""
import setuptools
import os

try:
    from sphinx.setup_command import BuildDoc

    cmdclass = {"build_sphinx": BuildDoc}
except ModuleNotFoundError:
    pass


def long_desc(path_to_md):
    """
    Use README.md for description.
    """
    with open(path_to_md, "r") as _fh:
        return _fh.read()


setuptools.setup(
    name="Flask-Commonmark",
    version="0.7",
    url="https://gitlab.com/doug.shawhan/flask-commonmark",
    project_urls={
        "Bug Tracker": "https://gitlab.com/doug.shawhan/flask-commonmark/issues",
        "Source Code": "https://gitlab.com/doug.shawhan/flask-commonmark/tree/master",
        "Development Version": "https://gitlab.com/doug.shawhan/flask-commonmark/tree/dev",
        "Documentation": "https://flask-commonmark.readthedocs.io",
    },
    license="BSD",
    author="Doug Shawhan",
    author_email="doug.shawhan@gmail.com",
    maintainer="Doug Shawhan",
    maintainer_email="doug.shawhan@gmail.com",
    description="Add commonmark processing filter to your Flask app.",
    long_description=long_desc("README.md"),
    long_description_content_type="text/markdown",  # use mimetype for pretty!
    include_package_data=True,
    py_modules=["flask_commonmark"],
    platforms="any",
    install_requires=["Flask", "commonmark",],
    test_suite="nose.collector",
    tests_require=["nose"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
