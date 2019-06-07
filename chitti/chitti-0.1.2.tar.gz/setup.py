import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='chitti',
    version='0.1.2',
    author="Raja Mohan Reddy",
    author_email="rajamohanrdy@gmail.com",
    description="Python utility packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raja-1996",
    packages=setuptools.find_packages(),
    classifiers=[
     "Programming Language :: Python :: 3",
     "License :: OSI Approved :: MIT License",
     "Operating System :: OS Independent",
    ],
    install_requires=[
          'colorama',
    ]
 )