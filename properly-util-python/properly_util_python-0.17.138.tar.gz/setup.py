import setuptools
import os

major = 0
minor = 17
build_num = os.environ.get('PROPERLY_BUILD_NUMBER', '0-dev')

VERSION_TEMPLATE = "{}.{}.{}"
version_val = VERSION_TEMPLATE.format(major, minor, build_num)



setuptools.setup(
    name="properly_util_python",
    version=version_val,
    author="GoProperly",
    author_email="info@goproperly.com",
    description="Utility and helper functions for common Properly operations in python.",
    long_description="public",
    long_description_content_type="text/markdown",
    url="https://github.com/GoProperly/properly-util-python",
    packages=setuptools.find_packages(exclude=["custom_scripts", "tests"]),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
)
