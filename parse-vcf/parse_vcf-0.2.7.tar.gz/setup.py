from setuptools import setup
setup(
    name = "parse_vcf",
    packages = [""],
    version = "0.2.7",
    description = "Variant Call Format parser and convenience methods",
    author = "David A. Parry",
    author_email = "david.parry@igmm.ed.ac.uk",
    url = "https://github.com/david-a-parry/parse_vcf.py",
    download_url = 'https://github.com/david-a-parry/parse_vcf.py/archive/0.2.7.tar.gz',
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=['pysam'],
    python_requires='>=3',
    license='MIT',
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        ],
)
