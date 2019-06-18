import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytensors",
    version="0.10.0",
    author="Anthony Potappel",
    author_email="anthony.potappel@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="Interact with Python Tensors",
    url="https://github.com/tensorframe/pytensors",
    packages=setuptools.find_packages(),
    #python_requires='~=3.5, ~=3.6, ~=3.7',
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
