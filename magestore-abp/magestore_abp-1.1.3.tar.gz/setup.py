import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

package_name = 'magestore_abp'
packages = setuptools.find_packages(include=[package_name, "{}.*".format(package_name)])

setuptools.setup(
    name=package_name,
    version="1.1.3",
    author="Mars",
    author_email="mars@trueplus.vn",
    description="Compress package with smaller size than before",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://magestore.com",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3',
    include_package_data=True
)
