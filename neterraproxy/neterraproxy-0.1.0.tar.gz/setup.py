import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neterraproxy",
    version="0.1.0",
    author="Anton Nanchev",
    author_email="ananchev@gmail.com",
    description="A python version of the neterra proxy java app written by @sgloutnikov",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ananchev/neterraproxy",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'bs4',
        'apscheduler'
    ],
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)