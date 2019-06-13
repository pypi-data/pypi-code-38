import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="interpret_segmentation",
    version="1.0.0",
    author="Fabio Anderegg",
    author_email="andef4@bfh.ch",
    description="Interpreing image segmentation models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=['interpret_segmentation.hdm', 'interpret_segmentation.rise'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Pillow",
        "matplotlib",
        "numpy",
        "scipy",
        "tqdm",
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
            'pre-commit',
            'sphinx',
            'sphinx_rtd_theme',
        ]
    }
)
