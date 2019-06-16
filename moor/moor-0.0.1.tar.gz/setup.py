from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="moor",
    version="0.0.1",
    author="Ed FitzGerald",
    author_email="edward.fitzgerald@fetch.ai",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ejfitzgerald/moor",
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['toml'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'pytest'],
    },
    entry_points={
        'console_scripts': [
            'moor = moor.cli:main'
        ],
    },
)
