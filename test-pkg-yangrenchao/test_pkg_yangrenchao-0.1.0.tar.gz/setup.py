import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="test_pkg_yangrenchao",
    version="0.1.0",
    author="Somebody",
    author_email="somebody@python123.io",
    description="An example for PY84 Courses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/somebody/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)