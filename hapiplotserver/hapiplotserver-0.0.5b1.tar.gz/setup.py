from setuptools import setup, find_packages
import sys

install_requires = ["hapiclient>0.0.8", "Flask==1.0.2", "gunicorn==19.9.0", "matplotlib>=2.2.2"]

if len(sys.argv) > 1 and sys.argv[1] == 'develop':
    install_requires.append("Pillow")

# version is modified by misc/version.py. See Makefile.
setup(
    name='hapiplotserver',
    version='0.0.5b1',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/hapiplotserver/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    include_package_data=True,
    scripts=["hapiplotserver/hapiplotserver"] 
)

























































