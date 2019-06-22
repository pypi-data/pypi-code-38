from distutils.core import setup


setup(
    name='django-mint',
    packages=['mint'],
    version='0.54',
    description='RESTful API for Django',
    author='Michael Bates',
    author_email='michael@mbates.co',
    url='https://github.com/pastapreneur/mint',
    download_url='https://github.com/pastapreneur/mint/tarball/0.47',
    keywords=['django', 'api', 'rest', 'restful'],
    classifiers=[],
    install_requires=['python-dateutil']
)