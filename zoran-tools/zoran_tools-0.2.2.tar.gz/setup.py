
from setuptools import setup


setup(
    name='zoran_tools',
    version='0.2.2',
    author='bkiu',
    author_email='chenzhongrun@bonc.com.cn',
    description='自用的一些小工具,包括列出文件夹下的文件, 读写CSV等',
    packages=['zoran_tools', 'zoran_tools.calculate', 'zoran_tools.frame', 'zoran_tools.frame.frame',
              'zoran_tools.frame.tools'],
)
