import setuptools


with open("requirements.txt") as fh:
    reqs = fh.read()


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="dwl",
    author="xliiv",
    author_email="tymoteusz.jankowski@gmail.com",
    description="Stupid command to download YouTube's `watch later` videos.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=reqs,
    url="https://gitlab.com/xliiv/dwl",
    py_modules=['dwl'],
    scripts=['bin/dwl'],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
