import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


# get the long description from the README file
with open(os.path.join(here, "README.md"), "r", encoding='utf-8') as f:
    long_descripton = f.read()


setup(
        name="pyhandy",
        version="0.0.3",
        author="callmexss",
        author_email="callmexss@126.com",
        description="A collection of python tools to make my life easier.",
        long_descripton=long_descripton,
        long_descripton_content_type="text/markdown",
        url="https://github.com/callmexss/pyhandy",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3.6",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent"
            ],
        packages=find_packages(exclude=['tests', 'docs']),
        python_requires='>=3.6',
        entry_points={
            'console_scripts': [
                'pyhandy=pyhandy:main',
                ],
            },
        )
