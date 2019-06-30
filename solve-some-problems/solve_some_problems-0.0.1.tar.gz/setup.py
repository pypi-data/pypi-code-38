from setuptools import setup

setup(
    # 发布到PyPI后的package name
    name='solve_some_problems',
    # 版本号
    version='0.0.1',
    # 描述
    description='Used to solve some mathematical problems.',
    # 如果要发布的项目只包含模块，那就指定py_modules这个关键字参数
    py_modules=['solve_mathematical_problems']
)
