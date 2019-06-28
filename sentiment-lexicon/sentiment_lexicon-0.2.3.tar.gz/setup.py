from setuptools import setup

with open('./README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='sentiment_lexicon',
    version='0.2.3',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=['sentiment_lexicon'],
    url='https://github.com/emilbaekdahl/sentiment_lexicon',
    author='Emil Bækdahl',
    author_email="emilsbaekdahl@gmail.com",
    project_urls={'Source Code': 'https://github.com/emilbaekdahl/sentiment_lexicon',
                  'Documentation': 'https://emilbaekdahl.github.io/sentiment_lexicon/'},
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers', 'License :: OSI Approved :: MIT License']
)
