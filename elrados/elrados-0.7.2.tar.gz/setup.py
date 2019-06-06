"""Setup file for handling packaging and distribution."""
import sys

from setuptools import setup, find_packages

__version__ = "0.7.2"

requirements = [
    'django>=1.8,<1.9',
    'twisted',
    'crochet',
    'autobahn',
    'rotest>=7.0.0',
]

setup(
    name='elrados',
    version=__version__,
    description="Frontend for django models and Rotest Testing Framework",
    license="MIT",
    author="Elran Shefer",
    author_email="elran777@gmail.com",
    url="https://github.com/IamShobe/elrados",
    keywords="rotest frontend",
    install_requires=requirements,
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"elrados": ["static/*",
                              "static/img/*",
                              "static/font/*",
                              "templates/*"]},
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        ],
    entry_points={
        "rotest.cli_server_actions":
            ["elrados_server = elrados.backend.main:setup_server"],
        "elrados.plugins": []
    },
)
