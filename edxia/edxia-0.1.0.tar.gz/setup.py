from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='edxia',
    version='0.1.0',
    description='SEM-BSE-EDS image analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/specmicp/eds_bse_corr/',
    author='Fabien Georget',
    author_email='Fabien.georget@epfl.ch',  # Optional
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='SEM EDS BSE visualization',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.4, <4',
    install_requires=[
            'glueviz',
            'pandas',
            'py_expression_eval',
            'scikit-image',
            'scikit-learn'
            ],

    extras_require={},

    package_data={'': ['*.ui'],},
    data_files=[],
    entry_points="""
        [glue.plugins]
        edxia=edxia:setup
        """,
    project_urls={
        'Funding': 'https://lmc.epfl.ch/'
    },
)
