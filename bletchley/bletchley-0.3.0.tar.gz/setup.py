import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bletchley",
    version="0.3.0",
    author="manny",
    author_email="manny@cyber-wizard.com",
    description="A collection of historical ciphers and cryptanalysis tools",
    license="GPL version 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/manny_cyber_wizard/bletchley",
    keywords = "cryptography ciphers cryptanalysis historical",
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=[
        "numpy>=1.16.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Development Status :: 3 - Alpha",
    ],
    project_urls={ 
        'Bug Reports': 'https://gitlab.com/manny_cyber_wizard/bletchley/issues',
        'Say Thanks!': 'https://saythanks.io/to/MannyCyber',
        'Source': 'https://gitlab.com/manny_cyber_wizard/bletchley',
    },
)