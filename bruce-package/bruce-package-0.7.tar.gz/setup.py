from setuptools import setup, Extension

setup(
    name = 'bruce-package',
    version = '0.7',
    description = 'GPU-accelerated binary star model',
    url = None,
    author = 'Samuel Gill et al',
    author_email = 'samuel.gill@warwick.ac.uk',
    license = 'GNU',
    packages=['bruce','bruce/binarystar'],
    scripts=['Utils/ngtsfit/ngtsfit',
             'Utils/lcbin/lcbin',
             'Utils/tessget/tessget',
             'Utils/tls/tls',
             'Utils/prewhiten/prewhiten',
             'Utils/mbls/mbls',
             'Utils/analyse/analyse',
             'Utils/massfunc/massfunc',
             'Utils/modulation/modulation'],
    install_requires=['celerite', 'numba', 'numpy', 'emcee']
)