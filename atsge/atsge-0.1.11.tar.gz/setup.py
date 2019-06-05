import setuptools

def get_long_description():
    with open("README.md", 'r') as fh:
        long_description = fh.read()
    return long_description

def get_requirements():
    with open("requirements.txt", 'r') as fh:
        reqs = fh.read().splitlines()
    return reqs

setuptools.setup(
    name="atsge",
    version="0.1.11",
    author="Shane Breeze",
    author_email="sdb15@ic.ac.uk",
    scripts=[],
    description="SGE batch job submission with AlphaTwirl",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/shane-breeze/atsge",
    packages=setuptools.find_packages(),
    download_url="https://github.com/shane-breeze/atsge/archive/0.1.11.tar.gz",
    install_requires=get_requirements(),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
    ],
)
