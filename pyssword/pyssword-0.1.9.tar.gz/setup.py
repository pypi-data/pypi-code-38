import setuptools

setuptools.setup(
    name="pyssword",
    version="0.1.9",
    author="Corleo",
    author_email="corleo.git@gmail.com",
    description="A Python password generator.",
    packages=setuptools.find_packages(),
    install_requires=[
        'colorama',
        'click',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points='''
        [console_scripts]
        pyssword=pyssword.pyssword:run
    ''',
)
