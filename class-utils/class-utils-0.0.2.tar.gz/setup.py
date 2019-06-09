import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='class-utils',
    version='0.0.2',
    author='fly1ngDream',
    author_email='fly1ngDream@protonmail.com',
    description='Utils for simplifying work with classes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fly1ngDream/class-utils',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
