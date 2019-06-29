import setuptools

setuptools.setup(
    name="jackAudio",
    version="1.0.3",
    author="Cooper Barth",
    author_email="cooperfbarth@gmail.com",
    description="A Python package for stationary audio noise reduction.",
    long_description_content_type="text/markdown",
    url="https://github.com/cooperbarth/jack-audio",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'librosa',
        'pathlib',
        'pysndfx'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

'''
PACKAGING:
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/* --skip-existing
'''