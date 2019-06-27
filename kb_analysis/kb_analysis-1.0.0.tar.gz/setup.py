import setuptools
try:
    import pkg_utils
except ImportError:
    import pip._internal
    pip._internal.main(['install', 'pkg_utils'])
    import pkg_utils
import os

name = 'kb_analysis'
dirname = os.path.dirname(__file__)
file_patterns = ['**/*.col', '**/*.db', '**/*.xlsx', '**/*.xml']
##package_data = {
##    name: [
##        'VERSION',
##    ],
####    'data': file_patterns,
####    'model': file_patterns,
####    'recon_2_2': file_patterns,
####    'reconstruction': file_patterns,
##}

# get package metadata
md = pkg_utils.get_package_metadata(dirname, name)

# install package
setuptools.setup(
    name=name,
    version=md.version,
    description="H1 human embryonic stem cells (hESCs) Data Analysis",
    long_description=md.long_description,
    url="https://github.com/KarrLab/" + name,
    download_url='https://github.com/KarrLab/' + name,
    author="Karr Lab",
    author_email="karr@mssm.edu",
    license="MIT",
    keywords='whole-cell systems biology',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    package_data=md.package_data,
    entry_points={
        'console_scripts': [
            'data = data.__main__:main',
        ],
    },
    install_requires=md.install_requires,
    extras_require=md.extras_require,
    tests_require=md.tests_require,
    dependency_links=md.dependency_links,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)
