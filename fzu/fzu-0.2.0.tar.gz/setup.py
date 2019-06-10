import re
from setuptools import setup


def version():
    pyfile = 'fzu/__main__.py'
    with open(pyfile) as fp:
        data = fp.read()

    match = re.search(r"__version__ = '([^']+)'", data)
    assert match, 'cannot find version in {}'.format(pyfile)
    return match.group(1)


setup(
    name='fzu',
    version=version(),
    description='Fuzzy unicode search',
    long_description=open('README.md').read(),
    author='Miki Tebeka',
    author_email='miki.tebeka@gmail.com',
    license='BSD',
    url='https://github.com/tebeka/fzu',
    packages=['fzu'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'fzu = fzu.__main__:main',
        ]
    },
)
