try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup # Fallback to distutils.

NAME = 'robotframework_openafslibrary'
exec(open('OpenAFSLibrary/__version__.py').read()) # get VERSION

setup(
    name=NAME,
    version=VERSION,
    description='Robot Framework test library for OpenAFS',
    long_description=open('README.rst').read(),
    author='Michael Meffie',
    author_email='mmeffie@sinenomine.net',
    url='https://github.com/openafs-contrib/robotframework-openafslibrary',
    license='BSD',
    packages=[
        'OpenAFSLibrary',
        'OpenAFSLibrary.keywords',
    ],
    install_requires=[
        'robotframework>=2.7.0',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
    ],
)

