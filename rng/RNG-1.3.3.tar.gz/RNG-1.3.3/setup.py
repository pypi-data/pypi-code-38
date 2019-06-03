from setuptools import setup, Extension
from Cython.Build import cythonize


with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="RNG",
    ext_modules=cythonize(
        Extension(
            name="RNG",
            sources=["RNG.pyx"],
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
    version="1.3.3",
    description="Python API for the C++ Random library",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
        "rng", "Mersenne Twister", "random number generator", "cpp random library", "random integer", "Bernoulli",
        "binomial", "negative_binomial", "geometric", "poisson", "discrete",
        "normal", "distribution", "log normal", "gamma", "exponential", "weibull", "extreme value",
        "chi squared", "cauchy", "fisher f", "student t",
    ],
    python_requires='>=3.7',
)
