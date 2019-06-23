import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'matplotlib'
]

setuptools.setup(
    name="smartwidgets",
    version="0.0.1",
    author="Ben Russell",
    author_email="bprussell80@gmail.com",
    description="Matplotlib widgets with improved appearance and options.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/benrussell80/smartwidgets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)