from setuptools import setup, Extension
from Cython.Build import cythonize


with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="Fortuna",
    ext_modules=cythonize(
        Extension(
            name="Fortuna",
            sources=["Fortuna.pyx"],
            language=["c++"],
            extra_compile_args=["-std=c++17", "-Ofast", "-march=native"],
        ),
        compiler_directives={
            'embedsignature': True,
            'language_level': 3,
        },
    ),
    author="Broken aka Robert Sharp",
    author_email="webmaster@sharpdesigndigital.com",
    url="https://sharpdesigndigital.com",
    requires=["Cython"],
    version="3.6.0",
    description="Custom Random Value Generators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["fortuna_extras"],
    license="Free for non-commercial use",
    platforms=["Darwin", "Linux"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Cython",
        "Programming Language :: C++",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "Fortuna", "Random Patterns", "Data Perturbation", "Game Dice", "Weighted Choice",
        "Random Value Generator", "Gaussian Distribution", "Linear Distribution",
        "TruffleShuffle", "FlexCat", "Percent True", "ZeroCool", "QuantumMonty",
        "Custom Distribution", "Rarity Table",
    ],
    python_requires='>=3.7',
)
