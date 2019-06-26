from distutils.core import setup
from setuptools import find_packages

setup(
    name='algonaut',
    python_requires='>=3',
    version='0.0.1',
    author='Andreas Dewes',
    author_email='andreas.dewes@algoneer.org',
    license='GNU Affero General Public License - Version 3 (AGPL-3)',
    url='https://github.com/algoneer/algonaut',
    packages=find_packages(),
#    package_data={'': ['*.ini']},
    include_package_data=True,
    install_requires=[
        'psycopg2_binary==2.8.3',
        'celery==4.2.1',
        'cryptography==2.7',
        'click==6.7',
        'Flask==1.0.2',
        'pytz==2018.7',
        'PyYAML==3.12',
        'requests==2.18.4',
        'SQLAlchemy==1.2.7',
        'SQLAlchemy-Utils==0.33.3',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'algonaut = algonaut.cli.main:main'
        ]
    },
    description='The API toolkit for Algoneer.',
    long_description="""The API toolkit for Algoneer.
"""
)
