import setuptools

setuptools.setup(
    name="pyquake",
    version="1.0.3",
    author="Cooper Barth",
    author_email="cooperfbarth@gmail.com",
    description="A package enabling the synthesis of seismic audio.",
    long_description_content_type="text/markdown",
    url="https://github.com/cooperbarth/PyQuake",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'urllib',
        'mpu'
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
python -m twine upload dist/*
'''