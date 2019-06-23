import setuptools

import time_me

setuptools.setup(
    name=time_me.__name__,
    version=time_me.__version__,
    author=time_me.__author__,
    packages=['time_me'],
    extras_requiew={
        'bar plots': ['matplotlib']
    },
    python_requires='>=3.7.0',
)
