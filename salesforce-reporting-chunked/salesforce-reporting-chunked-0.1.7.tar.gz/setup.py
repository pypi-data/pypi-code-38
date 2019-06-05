import setuptools
import os
try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {"build_sphinx": BuildDoc}
except ImportError:
    pass

def long_desc(path_to_md):
    """
    Use markdown for description on devpi server.
    """
    with open(path_to_md, "r") as _fh:
        return _fh.read()

setuptools.setup(
    name = "salesforce-reporting-chunked",
    version = "0.1.7",
    description = "Get > 2000 records from Salesforce reports with python.",
    long_description=long_desc("README.md"),
    long_description_content_type="text/markdown", # use mimetype!
    author = "Doug Shawhan",
    author_email = "doug.shawhan@gmail.com",
    maintainer = "Doug Shawhan",
    maintainer_email = "doug.shawhan@gmail.com",
    url="https://gitlab.com/doug.shawhan/salesforce-reporting-chunks",
    keywords = ["python", "salesforce", "salesforce.com"],
    install_requires= [
      "requests",
      "salesforce-reporting",
    ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
    ],
    include_package_data=True,
    packages=setuptools.find_packages(),
    zip_safe=True,
    license="MIT License",
    project_urls={
        "Documentation": "https://salesforce-reporting-chunks.readthedocs.io",
        "Bug Tracker": "https://gitlab.com/doug.shawhan/salesforce-reporting-chunks/issues",
        "Source Code": "https://gitlab.com/doug.shawhan/salesforce-reporting-chunks",
        "Development Version": "https://gitlab.com/doug.shawhan/salesforce-reporting-chunks/tree/dev",
    },
)
