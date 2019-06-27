from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="picorg",
    version="0.1.0",
    description="A script that helps you organize your pictures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["picorg", "timestamp_finder", "rename", "duplicates", "settings"],
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pillow", "exifread"],
    url="https://github.com/frangiz/picorg",
    author="Björn Olsson Jarl",
    author_email="frangiz@gmail.com",
    entry_points={"console_scripts": ["picorg = picorg:main"]},
    python_requires=">=3.6",
)
