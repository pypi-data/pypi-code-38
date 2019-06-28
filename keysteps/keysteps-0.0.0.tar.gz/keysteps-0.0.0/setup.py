from setuptools import setup

long_description = None
with open('README.md') as f:
    long_description = f.read()

setup(
    name='keysteps',
    packages=['keysteps'],
    version='0.0.0',
    license='MIT',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nosarthur/keysteps',
    platforms=['linux', 'osx', 'win32'],
    keywords=['keyboard layout', ''],
    author='Dong Zhou',
    author_email='zhou.dong@gmail.com',
    entry_points={'console_scripts': ['keysteps= keysteps.__main__:main']},
    python_requires='~=3.6',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Terminals",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    include_package_data=True,
)
