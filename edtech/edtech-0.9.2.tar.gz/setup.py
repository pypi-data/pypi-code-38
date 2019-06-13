from distutils.core import setup

setup(
    name='edtech',
    version='0.9.2',
    packages=['edtech',],
    url='https://github.com/misterjei/etlib',
    license='GPL 3',
    author='Jeremiah Blanchard',
    author_email='jblanch@cise.ufl.edu',
    description='Tool project from educational technology group',
    install_requires=['configparser','PySide2', 'urllib3', 'xlrd', 'xlwt']
)
