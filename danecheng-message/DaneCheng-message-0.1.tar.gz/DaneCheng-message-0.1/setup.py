# coding UTF-8 #定义程序的编码
# 通过 setuptools 模块导入所需要的函数
from setuptools import setup,find_packages
setup(
    name="DaneCheng-message",
    version = "0.1",
    author = "DaneCheng",
    #url = "www.baidu.com",
    packages = find_packages("src"),  # src 就是模块的保存目录
    package_dir = {"":"src"}, # 告诉 setuptools 包都在src 下
    package_data = { # 配置其他的文件的打包处理
    # 任何包中含有 .txt 文件，都包含它
    "":["*.txt","*.info","*.properties"],
    # 包含 demo 包 data 文件夹中的 *.dat 文件
    "":["data/*.*"],
    },
    exclude = ["*.test","*.test","*.test","*.test"], # 取消所有的测试包
)