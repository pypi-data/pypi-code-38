from setuptools import setup


setup(
    name='todoit',
    version='1.0',
    description='CLI todo list',
    author='Enkot',
    install_requires=['click', 'peewee', 'merry'],
    entry_points={
        'console_scripts': [
            'todoit=todoit:cli',
        ]
    },
)
