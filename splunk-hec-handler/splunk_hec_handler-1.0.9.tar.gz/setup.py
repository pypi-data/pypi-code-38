from setuptools import setup

setup(
    name='splunk_hec_handler',
    version='1.0.9',
    license='MIT License',
    description='A Python logging handler to sends logs to Splunk using HTTP event collector (HEC)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='vavarachen',
    author_email='vavarachen@gmail.com',
    url='https://github.com/vavarachen/splunk_hec_handler',
    packages=['splunk_hec_handler'],
    install_requires=['requests >= 2.6.0, < 3.0.0', 'requests'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Logging'
    ]
)
