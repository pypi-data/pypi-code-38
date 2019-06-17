import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thanos-snap",
    version="0.0.1",
    author="AbiramK",
    author_email="AbiramK@gitlab.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/AbiramK/thanos-snap",
    packages=["thanos"],
    entry_points={
        "console_scripts":['thanos = thanos.thanos:main']
        },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
