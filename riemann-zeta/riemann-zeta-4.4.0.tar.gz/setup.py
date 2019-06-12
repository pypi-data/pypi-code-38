from setuptools import setup, find_packages

setup(
    name='riemann-zeta',
    version='4.4.0',
    author='James Prestwich',
    license='LGPL',
    packages=find_packages(),
    package_data={'zeta': ['py.typed']},
    package_dir={'zeta': 'zeta'},
    install_requires=[
        'connectrum',
        'riemann-tx>=2.0.0',
        'ecdsa',
        'pycryptodomex'],
    tests_require=[
        'tox',
        'mypy',
        'flake8',
        'pytest',
        'pytest-cov'],
    python_requires='>=3.6'
)
