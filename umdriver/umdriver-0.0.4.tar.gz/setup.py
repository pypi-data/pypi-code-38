import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='umdriver',
    version='0.0.4',
    author='Jamie Davis',
    author_email='jamjam@umich.edu',
    description=(
        'An extension of the selenium webdriver bindings for python '
        'with U-M weblogin baked in.'),
    install_requires=[
        'selenium',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jamie-r-davis/umdriver',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3'
    ]
)
