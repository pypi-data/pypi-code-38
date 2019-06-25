import json
from setuptools import setup

with open('requirements.txt') as f:
    requires = list(filter(lambda x: bool(x), map(lambda x: x.strip(), f.readlines())))

with open('info.json') as f:
    info = json.load(f)
    
setup(
    name='volcano-web',
    version=info['version'],
    description='Web server satellite for Volcano',
    author='Vinogradov D',
    author_email='dgrapes@gmail.com',
    license='MIT',
    packages=['volcano.web'],
    package_data={'': ['www/*.*', 'www/ext/angular/*', 'www/ext/bootstrap3/css/*', 'www/ext/bootstrap3/fonts/*', 'www/ext/bootstrap3/js/*',
                       'www/ext/jquery/*']},
    zip_safe=False,
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
