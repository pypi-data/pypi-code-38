import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="pysge",
    version="0.1.0",
    author="Shane Breeze",
    author_email="sdb15@ic.ac.uk",
    scripts=["pysge/pysge_worker.py", "pysge/pysge_worker.sh"],
    description="python interface to submit functions to an SGE batch cluster",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shane-breeze/pysge",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
    ),
)
