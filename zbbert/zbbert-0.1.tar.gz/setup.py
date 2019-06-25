from setuptools import find_packages, setup
setup(
    name='zbbert',
    version='0.1',
    description='Python API for NER task',
    author='wgh',#作者
    author_email='1272599042@qq.com',
    #packages=find_packages(),
    packages=['zbbert'],  #这里是所有代码所在的文件夹名称
    install_requires=[ 'Twisted>=13.1.0',
        'w3lib>=1.17.0',
        'queuelib',
        'lxml',
        'pyOpenSSL',
        'cssselect>=0.9',
        'six>=1.5.2',
        'parsel>=1.1',
        'PyDispatcher>=2.0.5',
        'service_identity',],
)
