from pathlib import Path
from setuptools import setup
from typedconfig_awssource.__version__ import __version__

# The text of the README file
readme_text = Path(__file__).with_name("README.md").read_text()

setup(
    name='typed-config-aws-sources',
    version=__version__,
    description='AWS config sources for the typedconfig package',
    long_description=readme_text,
    long_description_content_type='text/markdown',
    url='https://github.com/bwindsor/typed-config-aws-sources',
    author='Ben Windsor',
    author_email='',
    python_requires='>=3.6.0',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Typing :: Typed',
    ],
    packages=['typedconfig_awssource'],
    include_package_data=True,
    install_requires=[
        'boto3',
        'typed-config'],
    entry_points={}
)
