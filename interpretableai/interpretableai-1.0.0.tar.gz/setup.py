from setuptools import setup
import os


def readme():
    with open('README.md') as f:
        return f.read()


VERSION = '1.0.0'
# Append build number to version if supplied
build_number = os.getenv('TWINE_BUILD_NUMBER')
if build_number:
    VERSION += '-' + build_number


setup(
    name='interpretableai',
    version=VERSION,
    description='Interface to Interpretable AI modules in Python',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://docs.interpretable.ai/IAI-Python/stable/',
    author='Interpretable AI',
    author_email='info@interpretable.ai',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    packages=['interpretableai'],
    install_requires=[
        'julia>=0.3',
        'pandas>=0.23',
        'future',
    ],
    include_package_data=True,
    zip_safe=False,
)
