import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

package_name = 'magestore_aup'
packages = setuptools.find_packages(
    include=[package_name, "{}.*".format(package_name)]
)

setuptools.setup(
    name=package_name,
    version="2.1.10",
    author="Mars",
    author_email="mars@trueplus.vn",
    description="Fix arguments missing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://magestore.com",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3',
    install_requires=[
        'cryptography==2.4.2',
        'fabric'
    ],
    include_package_data=True
)
