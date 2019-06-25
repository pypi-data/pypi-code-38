from setuptools import setup, find_packages

setup(
    name='Nightingale-ORM',
    version='0.9.11',
    description=(
        '一个简单而小巧的orm工具，只用于生成sql和对象，而不依赖db驱动',
        'A simple and compact ORM tool that only generates SQL and objects, not DB drivers'
    ),
    long_description=open('README.rst','rb').read(),
    author='beincy',
    author_email='bianhui0524@sina.com',
    maintainer='卞辉(beincy)',
    maintainer_email='bianhui0524@sina.com',
    license='MIT',
    packages=['NightingaleORM'],
    platforms=["all"],
    url='https://github.com/beincy/Nightingale-ORM',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)