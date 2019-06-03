from setuptools import setup, find_packages

from scurvysin import __doc__, __version__


options = dict(
    name='scurvysin',
    version=__version__,
    packages=find_packages(),
    license='MIT',
    description='Pip & conda wrapper / warper.',
    long_description=__doc__.strip(),
    author='Jan Pipek, Pavel Cahyna',
    author_email='jan.pipek@gmail.com',
    url='https://github.com/pythomec/scurvysin',
    python_requires="~=3.6",
    entry_points = {
        'console_scripts' : [
            "scurvy=scurvysin.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ]
)
setup(**options)

