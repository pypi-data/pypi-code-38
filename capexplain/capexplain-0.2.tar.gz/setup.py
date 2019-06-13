try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

from setuptools import find_packages

# Long description is github readme
long_description = None
with open('README.md') as f:
    long_description = f.read()

PACKAGE = 'capexplain'
VERSION = '0.2'

setup(
    name=PACKAGE,
    version=VERSION,
    author='US <e@g.com>',
    author_email='who@gmail.com',
    url='https://github.com/iitdbgroup/cape',
    install_requires=[
        'certifi>=2018.4.16',
        'chardet>=3.0.4',
        'colorful>=0.4.1',
        'geopy',
        'idna>=2.7',
        'numpy>=1.14.5',
        'pandas==0.23.4',
        'patsy>=0.5.0',
        'pkginfo>=1.4.2',
        'psycopg2-binary>=2.7.6',
        'python-dateutil>=2.7.3',
        'pytz>=2018.5',
        'requests>=2.19.1',
        'requests-toolbelt>=0.8.0',
        'scikit-learn>=0.19.2',
        'scipy>=1.1.0',
        'six>=1.11.0',
        'sklearn>=0.0',
        'SQLAlchemy==1.2.10',
        'statsmodels>=0.9.0',
        'tqdm>=4.23.4',
        'urllib3<1.24,>=1.23',
        'pandastable'
    ],

    entry_points={
        'console_scripts': [
            'capexplain=capexplain.cape:main',
            'capegui=capexplain.gui.Cape_GUI:main'
        ]
    },

    description='Cape - a system for explaining outliers in aggregation results through counterbalancing.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=find_packages(),

    keywords='db',
    platforms='any',
    license='Apache2',

    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',

        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',

        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
