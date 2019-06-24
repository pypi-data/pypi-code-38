from setuptools import setup,find_packages
with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='ThinkingDataSdk',
    version='1.1.23',
    description=(
        'This is the official Python SDK for ThinkingData Analytics SDK.'
    ),
    author='quanjie',
    author_email='quanjie@thinkingdata.cn',
    maintainer='quanjie',
    maintainer_email='quanjie@thinkingdata.cn',
    url='http://www.thinkingdata.cn',
    license='BSD License',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms=["all"],
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
    install_requires=[
        'requests',
    ],
)
