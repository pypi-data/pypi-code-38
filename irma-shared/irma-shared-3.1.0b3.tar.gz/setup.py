from setuptools import setup
from src import __version__

setup(
    name="irma-shared",
    version=__version__,
    author="irma-dev",
    author_email="irma-dev@quarkslab.com",
    description="Objects and well-known values used by the IRMA software",
    packages=(
        "irma.shared",
        "irma.shared.schemas",
    ),
    package_dir={
        "irma.shared": "src",
    },
    namespace_packages=(
        "irma",
    ),
    install_requires=(
        'marshmallow==3.0.0rc4',
    ),
    test_suite='nose.collector',
    tests_require=(
        'nose',
    )
)
