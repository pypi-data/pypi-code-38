import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-mail",
    version="0.0.3",
    author="PVladimir",
    author_email="vladimir.podolyan64@gmail.com",
    description="gmail client for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VladimirPodolyan/py-mail",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
