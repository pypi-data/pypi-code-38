import io
from setuptools import Extension, setup

try:
    from Cython.Distutils import build_ext
    cmdclass = {'build_ext': build_ext}
    ext_modules = [Extension('crc_itu', ['crc_itu.pyx'])]
except ImportError:
    cmdclass = {}
    ext_modules = []

setup(
    name='CRC-ITU',
    version='0.3.3',
    url='https://github.com/ak64th/CRC-ITU',
    author='Elmer Yu',
    author_email='ak64th@gmail.com',
    description='A crc-itu implementation with optional cython extension',
    long_description=io.open('README.rst', 'r', encoding='utf-8').read(),
    license='Apache 2.0',
    zip_safe=False,
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    py_modules=['crc_itu'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
