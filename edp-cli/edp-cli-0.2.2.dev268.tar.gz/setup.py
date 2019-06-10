import os
from setuptools import setup, find_packages

def prerelease_local_scheme(version):
    """Return local scheme version unless building on master in CircleCI.
    This function returns the local scheme version number
    (e.g. 0.0.0.dev<N>+g<HASH>) unless building on CircleCI for a
    pre-release in which case it ignores the hash and produces a
    PEP440 compliant pre-release version number (e.g. 0.0.0.dev<N>).
    """

    from setuptools_scm.version import get_local_node_and_date

    if 'CIRCLE_BRANCH' in os.environ and \
       os.environ.get('CIRCLE_BRANCH') == 'master':
        return ''
    else:
        return get_local_node_and_date(version)

setup(
    name='edp-cli',
    use_scm_version={
        'local_scheme': prerelease_local_scheme,
        'root': '..',
        'relative_to': __file__
    },
    setup_requires=['setuptools_scm'],
    description='A platform for the ingestion and management of experimental data.',
    long_description='A platform for the ingestion and management of experimental data.',
    url='https://github.com/OpenChemistry/edp',
    author='Kitware Inc',
    license='BSD 3-Clause',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(),
    install_requires=[
        'girder_client',
        'click',
        'pyparsing==2.2.0',
        'boto3',
        'bson',
        'pytz'
    ],
    entry_points= {
        'console_scripts': [
            'edp=edp.cli:cli'
        ]
    }
)
