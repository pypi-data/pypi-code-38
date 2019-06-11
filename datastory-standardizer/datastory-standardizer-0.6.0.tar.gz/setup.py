import setuptools

requires = ["pandas", "ddf_utils"]

setuptools.setup(
    name="datastory-standardizer",
    version="0.6.0",
    description="Harmonizing Datastory data",
    author="Robin Linderborg",
    author_email="robin@datastory.org",
    include_package_data=True,
    install_requires=requires,
    packages=setuptools.find_packages(),
)
