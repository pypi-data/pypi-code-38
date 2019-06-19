import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ucpbased",
    version="0.0.2",
    author="Zhamri Che Ani",
    author_email="zhamri@gmail.com",
    description="Use Case Points",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["UCP"],
    package_dir={'': 'ucpbased'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)