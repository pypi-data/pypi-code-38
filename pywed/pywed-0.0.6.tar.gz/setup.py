import os
import setuptools

# parse the requirements.txt
current_path = os.path.dirname(os.path.realpath(__file__))
requirements = []
with open(os.path.join(current_path, "requirements.txt")) as reqfile:
    for requirement in reqfile.read().splitlines():
        requirements.append(requirement)

setuptools.setup(
    name="pywed",
    version="0.0.6",
    author="Guillaume Vincke",
    author_email="guillaume.vincke@dice-engineering.com",
    description="PYthon client to d-ice WEthear Database",
    long_description="If you don't have a valid access key to the database, you won't be able to use this",
    url="https://d-ice.gitlab.host/common/python/pywed",
    packages=['wed'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)
