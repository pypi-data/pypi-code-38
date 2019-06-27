import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="naivenmt_datasets",
    version="0.0.6",
    description="A dataset utils repository. For tensorflow 2.x only!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/naivenmt/datasets",
    author="ZhouYang Luo",
    author_email="zhouyang.luo@gmail.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'deprecated >=1.2.5',
    ],
    license="MIT License",
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
