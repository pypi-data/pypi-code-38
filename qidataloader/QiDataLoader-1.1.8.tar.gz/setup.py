from setuptools import setup,find_packages

setup(
    name='QiDataLoader',
    version='1.1.8',
    description=(
        'ReadDataFromCustomByteData'
    ),
    # long_description=open('README.rst').read(),
    author='CarlSnow',
    author_email='carl.snow.china@gmail.com',
    maintainer='CarlSnow',
    maintainer_email='carl.snow.china@gmail.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    include_package_data = True,
    url='https://github.com/CarlSnow/FemasApi',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    # install_requires=[
    #     'Twisted>=13.1.0',
    #     'w3lib>=1.17.0',
    #     'queuelib',
    #     'lxml',
    #     'pyOpenSSL',
    #     'cssselect>=0.9',
    #     'six>=1.5.2',
    #     'parsel>=1.1',
    #     'PyDispatcher>=2.0.5',
    #     'service_identity',
    # ]
)