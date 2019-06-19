
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()


setup(
    name='pdf4me',
    version='0.8.17',
    description='Provides expert functionality to convert, optimize, merge, split, ocr, print documents & PDFs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://portal.pdf4me.com/',
    author='Pdf4me',
    author_email='support-dev@pdf4me.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Other/Nonlisted Topic',
        # license
        'License :: OSI Approved :: MIT License',
        # Supported python versions
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='pdf convert extract thumbnails merge optimize compress split stamp ocr archive',
    packages=find_packages(exclude=[]),
    # install_requires=['adal', 'inflection', 'requests', 'keyring', 'azure-mgmt-datalake-analytics', 'jprops'],
    install_requires=['inflection', 'requests', 'keyring', 'jprops' , 'six'],
    python_requires='>=2.7, <4',
    project_urls={
        # 'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
        'Bug Reports': 'https://github.com/pdf4me/pdf4me-clientapi-python/issues',
        'Source': 'https://github.com/pdf4me/pdf4me-clientapi-python',
    },
)
