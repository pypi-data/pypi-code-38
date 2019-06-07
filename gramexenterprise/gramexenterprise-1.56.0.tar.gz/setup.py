from setuptools import setup, find_packages
from glob import glob

setup(
    version="1.56.0",
    name="gramexenterprise",
    description="Gramex: Visual Analytics Platform (Enterprise version)",
    url="http://learn.gramener.com/guide/",
    author="Gramener",
    author_email="s.anand@gramener.com",
    license="Other/Proprietary License",
    keywords="gramex",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    packages=find_packages(),
    # Read: http://stackoverflow.com/a/2969087/100904
    # package_data includes data files for binary & source distributions
    # include_package_data is only for source distributions, uses MANIFEST.in
    package_data={
        'gramex': glob('gramexenterprise/handlers/*.html'),
    },
    include_package_data=True,
    install_requires=['gramex'],
    zip_safe=False,
)
