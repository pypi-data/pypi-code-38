import setuptools
from CrystalMatch.dls_imagematch.version import VersionHandler


# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    name = 'CrystalMatch',
    version = VersionHandler.version(),
    description = 'Python Toolkit for Matching Points on Formulatrix Images to Points on Beamline Images',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # see: https://dustingram.com/articles/2018/03/16/markdown-descriptions-on-pypi
    url='https://github.com/DiamondLightSource/CrystalMatch',
    author = 'Urszula Neuman',
    author_email = 'urszula.neuman@dimaond.ac.uk',
    license='Apache License 2.0',

    packages=[x for x in setuptools.find_packages() if x.startswith("CrystalMatch")],
    include_package_data = True,

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
    ],

    entry_points={'console_scripts': ['CrystalMatch = CrystalMatch.dls_imagematch.main_service:main']},  # this makes a script

    install_requires=['numpy>=1.11.1', 'scipy>=0.19.1', 'pygelf>=0.3.1'],

    tests_require=['mock>=1.0.1', 'parametrized'],

    zip_safe = False
)