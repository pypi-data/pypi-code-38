import setuptools

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rcvpapi",
    version="1.5.12",
    description="Module to interact with Arista CloudVision",
    url="https://github.com/networkRob/rcvp-api",
    author="Rob Martin",
    author_email="rjmarti88@icloud.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    zip_safe=False)