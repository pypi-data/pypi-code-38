import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="binho-host-adapter",
    version="0.1.1",
    author="Binho LLC",
    author_email="support@binho.io",
    description="Python Libraries for Binho Multi-Protocol USB Host Adapters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://binho.io",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyserial',

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)