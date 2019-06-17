import setuptools

setuptools.setup(
    name='jactPy',
    version='0.1.0',
    description='Just another crypto ticker in Python',
    url='http://github.com/milunski/jactPy',
    author='Matt Milunski',
    author_email='matthewmilunski@gmail.com',
    license='Apache 2.0',
    packages=setuptools.find_packages(),
    zip_safe=False, 
    install_requires=['requests']
)