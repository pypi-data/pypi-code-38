from setuptools import setup, find_packages

setup(
    name="KaUtil",
    version="1.0.2",
    keywords=("pip", "pathtool", "timetool", "magetool", "mage"),
    description="kaka util",
    long_description="kaka util",
    license="MIT Licence",
    url="",
    author="kaka zhang",
    author_email="zhangjiaying121@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['readability-lxml', 'lxml', 'requests'])
