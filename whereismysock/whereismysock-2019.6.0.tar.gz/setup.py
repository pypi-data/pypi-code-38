from setuptools import setup


setup(
    name='whereismysock',
    version='2019.6.0',
    description='A convenient way to work with websocket data streams',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    py_modules=['whereismysock'],
    author='Eugene Van den Bulke',
    author_email='eugene.vandenbulke@gmail.com',
    url='https://github.com/3kwa/whereismysock',
    install_requires=['lomond'],
    license='BSD',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
)
