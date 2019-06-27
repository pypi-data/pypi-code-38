import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-solc-simple",
    version="0.0.14",
    author="Paul Peregud",
    author_email="paulperegud@gmail.com",
    description="Simple wrapper around py-solc-x. Needs solc binary in PATH",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omisego/py-solc-simple",
    packages=setuptools.find_packages(),
    classifiers=(
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': ['py-solc-simple=solc_simple.builder:main'],
    },
    install_requires=[
        'py-solc-x==0.4.0'
    ],
    extras_require={
        'test': [
            "pytest>=4.4.0"
        ]
    }
)
