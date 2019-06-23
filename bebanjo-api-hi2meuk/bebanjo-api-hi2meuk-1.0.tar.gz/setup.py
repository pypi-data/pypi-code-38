import setuptools
import bebanjo

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bebanjo-api-hi2meuk",
    version=bebanjo.version,
    author="Steve Beaumont",
    author_email="steve@hi2.me.uk",
    description="A client library for interacting with Bebanjo's Movida and Seqeuence APIs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/hi2meuk/bebanjo-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
    python_requires='>=3',
)
