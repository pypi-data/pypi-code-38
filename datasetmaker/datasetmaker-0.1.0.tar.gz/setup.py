import setuptools

requires = ["ddf_utils", "pandas", "lxml", "requests",
            "pyarrow", "frame2package", "html5lib", "bs4"]

setuptools.setup(
    name="datasetmaker",
    version="0.1.0",
    description="Fetch, transform, and package data.",
    author="Robin Linderborg",
    author_email="robin@datastory.org",
    install_requires=requires,
    packages=setuptools.find_packages(),
)
