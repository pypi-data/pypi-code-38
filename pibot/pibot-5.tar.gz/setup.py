import setuptools
import subprocess

with open("README.md", "r") as fh:
    long_description = fh.read()

version = subprocess.run(['git', 'rev-list', '--all', '--count'], stdout=subprocess.PIPE)
version = version.stdout.decode('utf-8').replace('\n', '').replace('\r', '')

req = []
with open('requirements.txt', 'r') as file:
    for line in file:
        if line != '' or line != '\n':
            req.append(line)

setuptools.setup(
    name="pibot",
    version=version,
    author="TUC-RoboSchool",
    author_email="basti.neubert@gmail.com",
    description="Library for controlling the PiBot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuc-roboschool/PiBot",
    packages=setuptools.find_packages(),
    package_dir={'pibot': 'pibot'},
    install_requires=req,
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
)
