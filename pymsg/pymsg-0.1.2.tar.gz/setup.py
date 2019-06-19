import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='pymsg',
    version='0.1.2',
    url='https://github.com/Dog-Egg/pymsg',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lee',
    author_email='294622946@qq.com',
    py_modules=['pymsg'],
    install_requires=['requests']
)
