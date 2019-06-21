import setuptools

with open("doc/build/text/index.txt", "r", encoding='utf-8') as fh:
    long_description = fh.read()
    
if long_description is None:
	print("Error reading file")

setuptools.setup(
    name="qsdn",
    version="v0.0.0",
    author="Shawn.Pringle",
    author_email="shawn.pringle@gmail.com",
    description="Python Qt5 Classes that Display and Parse Numbers using Standard Decimal Notation",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://github.com/shawnpringle/separatorsafterdecimal",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'PyQt5',
    ],
    download_url="https://github.com/shawnpringle/separatorsafterdecimal/archive/v0.0.0.tar.gz",
)
