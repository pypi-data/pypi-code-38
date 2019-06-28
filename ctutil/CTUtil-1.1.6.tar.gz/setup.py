from setuptools import setup, find_packages

setup(
    name="CTUtil",
    version="1.1.6",
    keywords=("pip", "pathtool", "timetool", "magetool", "mage"),
    description="cingta django web util",
    long_description="cingta django web util",
    license="MIT Licence",
    url="https://github.com/JiaYingZhang/CTUtil",
    author="kaka zhang",
    author_email="zhangjiaying121@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'itsdangerous', 'pycryptodome', 'elasticsearch',
        'jinja2', 'redis'
    ],
    python_requires='>=3',
    data_filtes='template',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ], )
