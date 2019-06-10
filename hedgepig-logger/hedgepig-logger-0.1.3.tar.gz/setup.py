import setuptools
import hedgepig_logger

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='hedgepig-logger',
    version=hedgepig_logger.version,
    author='Denis Newman-Griffis',
    author_email='denis.newman.griffis@gmail.com',
    description='Lightweight logging in Python without timestamps or info labels.',
    long_description=long_description,
    long_description_context_type='text/markdown',
    url='http://github.com/drgriffis/hedgepig-logger',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
