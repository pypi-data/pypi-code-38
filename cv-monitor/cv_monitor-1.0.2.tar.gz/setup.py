from setuptools import setup, find_packages

setup(
    name='cv_monitor',
    version='1.0.2',
    keywords=('eos', 'btc', 'eth'),
    description='Monitor virtual currency through exchanges',
    license='MIT License',
    author='lovefive5',
    author_email='2845652616@qq.com',
    url='https://github.com/lovefive5/cv_monitor',
    platforms='any',
    include_package_data=True,
    packages=find_packages(),
    install_requires=['requests', 'pymysql']
)


# python setup.py bdist_egg
# python setup.py sdist
# twine upload dist/cv_monitor-1.0.1.tar.gz
