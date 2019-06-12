import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PySpoks",
    version="0.0.1",
    author="ElfanRodh",
    author_email="elfanapoywali@gmail.com",
    description="Sistem Pemeringkat Otomatis Berbasis Kata Sifat",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ElfanRodh/PySpoks",
    packages=setuptools.find_packages(),
    package_data={'spoks': ['data/*.json']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)