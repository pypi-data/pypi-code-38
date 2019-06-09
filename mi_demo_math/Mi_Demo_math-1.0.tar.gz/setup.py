from distutils.core import setup
setup(
    name='Mi_Demo_math',  # 对外我们模块的名字
    version='1.0',  # 版本号
    description='First test demo',  # 描述
    author='Venom',  # 作者
    author_email='Venom@163.com',
    py_modules=['Mi_Demo_math.math_add',
                'Mi_Demo_math.math_sub']  # 要发布的模块
)