from setuptools import setup

setup(
  name='toolstack',
  packages=['toolstack', 'toolstack.text', 'toolstack.feature', 'toolstack.utils'],  # this must be the same as the name above
  version='0.1.0-beta0',
  description='A collection of Useful tools to speed-up the data analysis process',
  author='Mohammed Yusuf Khan',
  author_email='hello@mykhan.me',
  url='https://github.com/getmykhan/toolstack', # use the URL to the github repo
  keywords=['toolkit', 'nlp', 'data cleaning', 'toolstack', 'data science', 'machine learning'],  # arbitrary keywords
  install_requires=['pandas', 'numpy'],
)
