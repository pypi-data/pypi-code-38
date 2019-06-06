import setuptools
import thompcoutils.version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thompcoutils",
    version=thompcoutils.version.version,
    author="Jordan Thompson",
    author_email="Jordan@ThompCo.com",
    description="Another collection of utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=[
        'psutil', 'netifaces'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

exclude_package_data = {'': ['install.sh']},
