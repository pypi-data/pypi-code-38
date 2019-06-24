from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file 
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

dtl_version = {}
with open("./datalogue/version.py") as fp:
    exec(fp.read(), dtl_version)

with open("./LICENSE", "r") as license_file:
    imported_license = license_file.read()
    setup(
        name="datalogue",
        version=dtl_version["__version__"],
        author="Nicolas Joseph",
        author_email="nic@datalogue.io",
        license=imported_license,
        description="SDK to interact with the datalogue platform",
        # long_description=long_description,
        # long_description_content_type="text/markdown",
        url="https://github.com/datalogue/dtl-python-sdk",
        packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
        classifiers=[
            "Programming Language :: Python :: 3",
            'Programming Language :: Python :: 3.6',
            "Operating System :: OS Independent"
        ],
        python_requires=">=3.6",
        install_requires=['requests', 'python-dateutil', 'validators', 'pytest==3.6.3', 'numpy', 'pyyaml', 'pyarrow', 'raven'],
        setup_requires=['pytest-runner'],
        tests_require=['pytest==3.6.3', 'pytest-cov==2.6.0']
)
