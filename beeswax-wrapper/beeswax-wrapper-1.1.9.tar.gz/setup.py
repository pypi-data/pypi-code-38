import os
from setuptools import setup, find_packages


about = {
    'here': os.path.abspath(os.path.dirname(__file__))
}

with open(os.path.join(about['here'], 'version.py')) as f:
    exec (f.read(), about)

try:
    with open(os.path.join(about['here'], 'test', '__init__.py')) as f:
        exec (f.read(), about)
except IOError:
    pass

with open(os.path.join(about['here'], 'README.md')) as f:
    about['readme'] = f.read()


setup(
    # available in PKG-INFO
    name='beeswax-wrapper',
    version=about['__version__'],
    description='Python Wrapper for the Beeswax API',
    url='https://github.com/iotgdev/beeswax_wrapper/',
    author='iotec',
    author_email='dev@dsp.io',
    license='MIT',
    download_url='https://github.com/iotgdev/beeswax_wrapper/archive/{}.tar.gz'.format(about['__version__']),
    long_description=about['readme'],
    long_description_content_type='text/markdown',
    platforms=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    # Package Properties
    packages=find_packages(include=['beeswax_wrapper', 'beeswax_wrapper.*']),
    include_package_data=True,
    test_suite='test',
    setup_requires=['pytest-runner'],
    tests_require=['mock>=2.0.0', 'pytest'],
    cmdclass={'pytest': about.get('PyTest')},
    scripts=['bin/beeswax_credentials'],
    install_requires=[
        'keyrings.alt>=3.1',
        'keyring==15.1.0',
        'requests>=2.19.1',
        'boltons>=18.0.0; python_version<"3.0"',
        'ujson>=1.35',
        'six>=1.11.0'
    ]
)
