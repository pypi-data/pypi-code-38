from setuptools import setup

setup(
    name='InstagramFakeAPI',
    version='0.1.2',
    description='Unofficial instagram API, build on LevPasha/Instagram-API-python. Give you access to ALL instagram features (like, follow, upload photo and video and etc)! Write on python.',
    url='https://github.com/endemic-ru/InstagramFakeAPI',
    author='Dmitriy Deniosv',
    author_email='mail@endemic.ru',
    license='GNU',
    packages=['InstagramFakeAPI'],
    zip_safe=False,
    install_requires=[
        "requests==2.11.1",
        "requests-toolbelt==0.7.0",
        "moviepy==0.2.3.2"
    ])
