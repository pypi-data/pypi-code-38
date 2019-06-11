#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 参考：https://packaging.python.org/tutorials/packaging-projects/
import setuptools
import send2trash
send2trash.send2trash(r'D:\atcy\.idea')
send2trash.send2trash(r'D:\atcy\build')
send2trash.send2trash(r'D:\atcy\dist')
send2trash.send2trash(r'D:\atcy\atcy.egg-info')


with open("README.rst", "r",encoding='utf-8') as fh:
    long_description = fh.read()
    print(long_description)

setuptools.setup(

    name="atcy-pkg-tcy",
    version="0.2.0",
    author="Tcy",
    author_email="979442421@qq.com",
    description="A small example package测试包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    # packages=setuptools.find_packages('atcy'),# 就表明只在”src”子目录下搜索所有的Python包
    # package_dir={'': 'atcy'},
    # packages=find_namespace_packages(include=['atcy.*']),
    keywords=("atcy",'Package_A1'),
    include_package_data=True,#https://docs.python.org/3.6/distutils/sourcedist.html
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],

)




# install_requires = [
#     'numpy>=1.11.1',
#     'matplotlib>=1.5.2',
#     'scipy>=0.18.0',
# ]

# classifiers = [
#     'Development Status :: 3 - Alpha',
#     'Topic :: Text Processing',
#     'License :: OSI Approved :: MIT License',
#     'Programming Language :: Python :: 3',
# ]
#
# test_suite = 'vaspy.tests.test_all'
#

# 生成源代码分发调用：python setup.py sdist


    # include_package_data=True, # 自动打包文件夹内所有数据
    # zip_safe=True,  # 设定项目包为安全，不用每次都检测其安全性
    # packages=find_packages(),
    # packages=find_namespace_packages(include=['Package.*']),

    # scripts=['say_hello.py'],



    # package_data={
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt','.log'],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    # },


# python setup.py sdist --formats=gztar,zip

# 创建wheel包：“python setup.py bdist_wheel”
# python setup.py install
# twine upload dist/*
# python setup.py install
# python setup.py bdist_egg
# python setup.py bdist_wininst

# pip3 install dist/Hello-1.0-py3-none-any.whl
# pip3 uninstall hello

# 分发setuptools基于项目的
# 有关分发setuptools项目的详细说明，请参阅 Packaging项目教程。
#
# 在开始之前，请确保您拥有最新版本的setuptools和wheel：
#
# python3 -m pip install --user --upgrade setuptools wheel
# 要构建setuptools项目，请从setup.py所在的同一目录运行此命令：
#
# python3 setup.py sdist bdist_wheel
# 这将在dist目录中生成分发存档。
#
# 在您上传生成的档案之前，请确保您已在https://test.pypi.org/account/register/上注册 。
# 您还需要验证您的电子邮件，以便能够上传任何软件包。您应该安装twine以便能够上传包：
#
# python3 -m pip install --user --upgrade setuptools wheel
# 现在，要上传这些档案，请运行：
#
# twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# 要安装新上传的软件包example_pkg，可以使用pip：
#
# python3 -m pip install --index-url https://test.pypi.org/simple/ example_pkg
# 如果您在任何时候遇到问题，请参阅包装项目教程 以获得澄清。