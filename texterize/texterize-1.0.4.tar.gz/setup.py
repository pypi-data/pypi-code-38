import setuptools

setuptools.setup(
    name="texterize",
    version="1.0.4",
    author="Cooper Barth",
    author_email="cooperfbarth@gmail.com",
    description="Making pictures worth a thousand words.",
    long_description_content_type="text/markdown",
    url="https://github.com/cooperbarth/texterize",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'python-docx',
        'pillow'
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