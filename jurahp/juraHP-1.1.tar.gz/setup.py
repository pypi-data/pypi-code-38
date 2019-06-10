import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='juraHP',
    version='1.1',
    url="https://johnnes-smarts.ch",
    license='License :: OSI Approved :: MIT License',
    author='David Johnnes',
    author_email='david.johnnes@gmail.com',
    description='SSH Client Framework for HP/Cisco AeroNet Interface Renaming',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='SSH Client, Network Automation',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
