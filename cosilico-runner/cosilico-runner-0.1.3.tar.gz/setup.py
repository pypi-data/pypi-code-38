import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cosilico-runner",
    version="0.1.3",
    author="Erik Storrs",
    author_email="epstorrs@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
#    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    entry_points={
        'console_scripts': [
            'cosilico-runner=cosilico_runner.cosilico_runner:main',
        ],
    },
)
