import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="protomaps",
    version="0.0.1",
    author="Protomaps",
    author_email="hi@protomaps.com",
    description="Interact with Protomaps API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://protomaps.com/docs/python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
