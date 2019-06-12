from setuptools import setup

with open("README.md") as f:
    readme = f.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python'
    ]

setup(
    name = "dilawar",
    version = "0.0.3",
    description = "My personal utilities. See the README.md file.",
    long_description = readme,
    packages = [ "dilawar" ],
    package_dir = { "dilawar" : 'src' },
    install_requires = [ ],
    author = "Dilawar Singh",
    author_email = "dilawars@ncbs.res.in",
    url = "http://github.com/dilawar/",
    license='GPL',
    classifiers=classifiers,
)
