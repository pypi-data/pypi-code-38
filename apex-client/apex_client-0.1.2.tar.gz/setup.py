import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="apex_client",
    version="0.1.2",
    author="Andréas Kühne",
    author_email="andreas.kuhne@promoteint.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/promoteinternational/apex-ng-client",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'apex_auth>=0.2.2',
        'django>=2.1.7',
        'python-dateutil>=2.8.0',
        'requests>=2.21.0'
    ]
)
