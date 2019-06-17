from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='py_proxy',
    version='0.2.6',
    packages=find_packages(),
    py_modules=["proxy"],
    install_requires=['requests', 'beautifulsoup4'],
    url='https://github.com/HOWZ1T/py_proxy',
    license='MIT License',
    author='HOWZ1T',
    author_email='dylan.d.randall@gmail.com',
    description='A proxy library for python 3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: Proxy Servers"
    ],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/HOWZ1T/py_proxy/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/HOWZ1T/py_proxy',
    },
)
