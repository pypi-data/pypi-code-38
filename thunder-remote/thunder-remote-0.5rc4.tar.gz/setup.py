import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thunder-remote",
    version="0.5rc4",
    author="Schrotty",
    author_email="rubenmaurer@live.de",
    description="A modified version of the 'pyController' package for usage with a ThunderBorg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Schrotty/thunder-remote",
    keywords="thunder-borg borg remote-control remote rc",
    packages=setuptools.find_packages(),
    install_requires=[
        'inputs',
        'events',
        'enum'
    ],
    license="MIT",
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
    ],
)
