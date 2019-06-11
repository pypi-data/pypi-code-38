from setuptools import setup

setup(
    # 以下为必需参数
    name='geecrack',  # 模块名
    version='1.0.0',  # 当前版本
    description='Crack the Geetest verification code',  # 简短描述
    py_modules=["geecrack"],  # 单文件模块写法
    # ckages=find_packages(exclude=['contrib', 'docs', 'tests']),  # 多文件模块写法

    # 以下均为可选参数
    long_description="",  # 长描述
    url='https://github.com/CrazyBunQnQ/GeetestCrack',  # 主页链接
    author='CrazyBunQnQ',  # 作者名
    author_email='crazybunqnq@gmail.com',  # 作者邮箱
    classifiers=[
        'Intended Audience :: Developers',  # 模块适用人群

        'License :: OSI Approved :: MIT License',  # 模块的license

        'Programming Language :: Python :: 3.6',  # 模块支持的Python版本
    ],
    keywords='geetest',  # 模块的关键词，使用空格分割
    install_requires=['selenium'],  # 依赖模块
    # extras_require={  # 分组依赖模块，可使用pip install sampleproject[dev] 安装分组内的依赖
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
    # package_data={  # 模块所需的额外文件
        # 'sample': ['package_data.dat'],
    # },
    # data_files=[('my_data', ['data/data_file'])],  # 类似package_data, 但指定不在当前包目录下的文件
    # entry_points={  # 新建终端命令并链接到模块函数
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    # project_urls={  # 项目相关的额外链接
    #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #     'Funding': 'https://donate.pypi.org',
    #     'Say Thanks!': 'http://saythanks.io/to/example',
    #     'Source': 'https://github.com/pypa/sampleproject/',
    # },
)
