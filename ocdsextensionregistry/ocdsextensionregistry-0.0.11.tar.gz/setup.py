from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocdsextensionregistry',
    version='0.0.11',
    author='Open Contracting Partnership',
    author_email='data@open-contracting.org',
    url='https://github.com/open-contracting/extension_registry.py',
    description="Eases access to information from the extension registry of the Open Contracting Data Standard",
    license='BSD',
    packages=find_packages(),
    long_description=long_description,
    install_requires=[
        'json-merge-patch',
        'requests',
    ],
    extras_require={
        'test': [
            'coveralls',
            'pytest',
            'pytest-cov',
        ],
        'docs': [
            'Sphinx',
            'sphinx-autobuild',
            'sphinx_rtd_theme',
        ],
        'cli': [
            'ocds-babel[markdown]>=0.1.0',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'ocdsextensionregistry = ocdsextensionregistry.cli.__main__:main',
        ],
    },
)
