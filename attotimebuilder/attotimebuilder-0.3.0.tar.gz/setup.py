from setuptools import setup, find_packages

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='attotimebuilder',
    version='0.3.0',
    description='A library for using the attotime datetime API with aniso8601',
    long_description=README_TEXT,
    author='Brandon Nielsen',
    author_email='nielsenb@jetfuse.net',
    url='https://bitbucket.org/nielsenb/attotimebuilder',
    install_requires=[
        'aniso8601>=5.0.0, <8.0.0',
        'attotime>=0.2.0, <0.3.0'
    ],
    packages=find_packages(),
    test_suite='attotimebuilder',
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='iso8601 attotime aniso8601 datetime',
    project_urls={
        'Documentation': 'https://attotimebuilder.readthedocs.io/',
        'Source': 'https://bitbucket.org/nielsenb/attotimebuilder',
        'Tracker': 'https://bitbucket.org/nielsenb/attotimebuilder/issues'
    }
)
