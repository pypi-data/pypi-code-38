import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

requirements = [
    'sklearn',
    'numpy',
    'matplotlib',
    'smartwidgets'
]

setuptools.setup(
    name="pixit",
    version="0.0.16",
    author="Ben Russell",
    author_email="bprussell80@gmail.com",
    description="Label and annotate images using matplotlib widgets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/benrussell80/pixit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    include_package_data=True,
)
