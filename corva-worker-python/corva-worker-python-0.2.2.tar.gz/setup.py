from setuptools import find_packages, setup


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries',
]

setup(
    name='corva-worker-python',
    author='Jordan Ambra, Mohammadreza Kamyab',
    author_email='jordan.ambra@corva.ai, m.kamyab@corva.ai',
    url='https://bitbucket.com/corva/corva-worker-python',
    version='0.2.2',
    classifiers=classifiers,
    description='SDK for interacting with Corva',
    keywords='corva',
    packages=find_packages(exclude=["test"]),
    install_requires=["numpy", "redis", "requests"],
    include_package_data=True,
    license='The Unlicense',
)
