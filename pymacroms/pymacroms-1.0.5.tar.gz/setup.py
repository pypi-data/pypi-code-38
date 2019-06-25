import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymacroms",
    version="1.0.5",
    author="Kevin De Bruycker and Tim Krappitz",
    author_email="kevindebruycker@gmail.com",
    description="pyMacroMS - High performance quantification of complex high resolution polymer mass spectra",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://macroarc.org/research/macroarc-pyMacroMS.html",
    license="MIT License",
    packages=setuptools.find_packages(),
    package_data={'pymacroms': ['RawFileReader/Unix/*', 'RawFileReader/Windows/*'], },
    install_requires=["IsoSpecPy>=1.9,<2", "matplotlib", "numpy", "pandas", "progressbar2", "pythonnet", "reportlab", "sklearn", "svglib>=0.9.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # python_requires='>=3.6',
)