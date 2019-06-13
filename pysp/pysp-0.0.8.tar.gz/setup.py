from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", 'r') as fd:
    version = fd.read().strip()

setup(
    name='pysp',
    version=version,
    description='Python-Support-Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='HyunSuk Lee',
    author_email='peanutstars.job@gmail.com',
    url='https://github.com/peanutstars/py-support-package',
    scripts=[],
    keywords='yaml configuration',
    packages=['pysp'],
    data_files = [('.', ['VERSION'])],
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Operating System Kernels :: Linux",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'PyYAML>=3.12',
        'SQLAlchemy>=1.2.14',
    ],
    setup_requires=[
    ],
)
