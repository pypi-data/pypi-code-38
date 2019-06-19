from setuptools import setup, find_packages

setup(
    name='some_utils',
    version="0.0.4",
    description=(
        'Some decorator utils for replacing function, retrying function... '
    ),
    long_description=open('README.rst').read(),
    author="zhangming",
    author_email="1570977353@qq.com",
    maintainer="zhangming",
    maintainer_email="1570977353@qq.com",
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url="",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ]
)