import setuptools

setuptools.setup(
    name = 'necstdb',
    version = __import__('necstdb').__version__,
    description = '',
    url = 'https://github.com/ogawa-ros/necstdb',
    author = 'Shota Ueda',
    author_email = 's7u27astr0@gmail.com',
    license = 'MIT',
    keywords = '',
    packages = [
        'necstdb',
    ],
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
