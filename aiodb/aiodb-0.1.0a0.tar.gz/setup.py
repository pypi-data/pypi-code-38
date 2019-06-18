import pathlib, re

from distutils.core import setup

here = pathlib.Path(__file__).parent

txt = (here / 'aiodb' / '__init__.py').read_text('utf-8')
try:
    version = re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
except IndexError:
    raise RuntimeError('Unable to determine version.')

def read(f):
    return (here / f).read_text('utf-8').strip()

setup(
    name='aiodb',
    packages=['aiodb'],
    version=version,
    description='Async database toolkit.',
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.rst'))),
    author='Jorge E. Cardona',
    author_email='jorgeecardona@gmail.com',
    maintainer='Jorge E. Cardona <jorgeecardona@gmail.com>',
    license='Apache 2',
    python_requires='>=3.5.3',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
