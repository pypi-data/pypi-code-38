import setuptools

setuptools.setup(
    name = 'pyinterface',
    version = __import__('pyinterface').__version__,
    description = 'driver for Interface PCI board',
    url = 'https://github.com/ogawa-ros/pyinterface',
    project_urls = {
        'Documentation': 'https://pyinterface.readthedocs.io/',
        'Source Code': 'https://github.com/ogawa-ros/pyinterface',
    },
    author = 'Atsushi Nishimura',
    author_email = 'ars096@gmail.com',
    license = 'MIT',
    keywords = '',
    packages = [
        'pyinterface',
    ],
    install_requires = [
        'portio',
        'pypci',
    ],
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware',
    ],
)
