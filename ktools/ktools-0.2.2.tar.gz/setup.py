import setuptools

setuptools.setup(
    name="ktools",
    version="0.2.2",
    url="https://github.com/fx-kirin/ktools",

    author="fx-kirin",
    author_email="ono.kirin@gmail.com",

    description="kirin's toolkit.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
