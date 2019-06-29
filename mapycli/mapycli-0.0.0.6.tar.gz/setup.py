from setuptools import setup, find_packages
import mapycli
setup(
    name='mapycli',
    version='0.0.0.6',
    description='Python module for client queries to OGC standard web services',
    url='https://github.com/Gabriel-Desharnais/Mapycli',
    author='Gabriel Desharnais',
    author_email='gabriel.desharnais@hotmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Atmospheric Science',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
        ],
    keywords='OWS OGC WMS WPS WFS WGS mapserver geoserver',
    packages=find_packages(),

    install_requires=['requests',],


    )
