from setuptools import setup, find_packages

setup(
    name='SmartDjango',
    version='2.0.2 beta',
    keywords=('django',),
    description='更高效率的Django开发[Chinese Version]',
    long_description='提供智能模型用于字段检测，函数返回类，错误类等',
    license='MIT Licence',
    url='https://github.com/lqj679ssn/SmartDjango',
    author='Adel Liu',
    author_email='i@6-79.cn',
    platforms='any',
    packages=find_packages(),
    install_requires=[
        'django',
    ],
)
