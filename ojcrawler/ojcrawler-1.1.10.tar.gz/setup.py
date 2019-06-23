from setuptools import setup, find_packages

with open("README.md", encoding='utf-8', mode="r") as fh:
    long_description = fh.read()

setup(
    name='ojcrawler',
    version='1.1.10',
    packages=find_packages(),
    url='https://github.com/LETTersOnline/ojcrawler',
    license='MIT',
    author='crazyX',
    author_email='xu_jingwei@outlook.com',
    description='crawler of some online judge system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['psutil', 'requests', 'robobrowser', 'beautifulsoup4', 'html5lib'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
