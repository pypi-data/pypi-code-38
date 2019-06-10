from setuptools import setup
import pathlib
from setuptools import setup
from mk8sconfig.main import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()
setup(
    name='microk8s-configure',
    version=__version__,
    packages=['mk8sconfig'],
    url='https://github.com/netsaj/microk8s-configure',
    license='MIT',
    description='Tool for configure microk8s on Ubuntu VPS',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        'paramiko==2.4.2',
        'cryptography==2.4.2',
        'termcolor==1.1.0',
        'tqdm==4.31.1',
    ],
    author='Fabio Moreno',
    author_email='fabiomoreno@outlook.com',
    entry_points={
        'console_scripts': [
            'mk8sconfig = mk8sconfig.main:main',
            'microk8s-configure= mk8sconfig.main:main',
        ],
    },
    scripts=['mk8sconf.py']
)
