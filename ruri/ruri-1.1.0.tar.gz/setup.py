import setuptools
from ruri import vars


with open("README.md", "r") as readme_file:
    readme_text = readme_file.read()

setuptools.setup(
    name="ruri",
    version=vars.VERSION,
    author="Tim van Leuverden",
    author_email="TvanLeuverden@Gmail.com",
    description="A CRC32 checker with file name checking.",
    long_description=readme_text,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Timmy1e/ruri",
    packages=setuptools.find_packages(),
    license="GPL-3",
    entry_points={
        'console_scripts': [
            'ruri=ruri.ruri:main'
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent"
    ],
)
