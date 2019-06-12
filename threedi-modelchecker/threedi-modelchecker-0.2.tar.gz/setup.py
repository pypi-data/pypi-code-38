from setuptools import setup

version = '0.2'

long_description = "\n\n".join([open("README.md").read(), open("CHANGES.md").read()])

install_requires = [
    "Click",
    "GeoAlchemy2>=0.6",
    "SQLAlchemy>=0.8",
    "threedigrid",
]

tests_require = [
    "factory_boy",
    "pytest",
    "mock",
    "pytest-cov"
]

setup(
    name="threedi-modelchecker",
    version=version,
    description="Checks validity of a threedi-model",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
    ],
    keywords=[],
    author="Richard Boon",
    author_email="richard.boon@nelen-schuurmans.nl",
    url="https://github.com/nens/threedi-modelchecker",
    license="MIT",
    packages=["threedi_modelchecker"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    entry_points={
        "console_scripts": [
            "threedi-modelchecker = threedi_modelchecker.scripts:check_model"
        ]
    },
)
