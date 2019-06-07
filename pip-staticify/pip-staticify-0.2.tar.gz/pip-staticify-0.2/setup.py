import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pip-staticify',
    version='0.2',
    scripts=['staticify'],
    author="Bart Machielsen",
    author_email="bartmachielsen@gmail.com",
    description="A python package for making your requirements static",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bartmachielsen/pip-staticify",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
