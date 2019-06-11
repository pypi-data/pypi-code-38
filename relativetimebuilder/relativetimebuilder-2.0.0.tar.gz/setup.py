from setuptools import setup, find_packages

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='relativetimebuilder',
    version='2.0.0',
    description='A library for using the dateutil relativedeltas for calendar precision with aniso8601',
    long_description=README_TEXT,
    author='Brandon Nielsen',
    author_email='nielsenb@jetfuse.net',
    url='https://bitbucket.org/nielsenb/relativetimebuilder',
    install_requires=[
        'aniso8601>=7.0.0, <8.0.0',
        'python-dateutil>=2.7.3'
    ],
    packages=find_packages(),
    test_suite='relativetimebuilder',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='iso8601 dateutil aniso8601 datetime',
    project_urls={
        'Documentation': 'https://relativetimebuilder.readthedocs.io/',
        'Source': 'https://bitbucket.org/nielsenb/relativetimebuilder',
        'Tracker': 'https://bitbucket.org/nielsenb/relativetimebuilder/issues'
    }
)
