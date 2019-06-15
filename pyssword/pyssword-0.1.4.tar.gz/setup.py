import setuptools

setuptools.setup(
    name="pyssword",
    version="0.1.4",
    author="Corleo",
    author_email="corleo.git@gmail.com",
    description="A Python password generator.",
    packages=setuptools.find_packages(),
    install_requires=[
        'corlorama',
        'click',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_requires=['pytest-runner'],
    tests_require=['pytest'],
)
