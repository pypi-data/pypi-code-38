from distutils.core import setup

setup \
(
    name='camel-case-switcher',
    version='2.0',
    packages=['camel_case_switcher'],
    url='https://gitlab.com/Hares/camel-case-switcher',
    download_url='https://gitlab.com/Hares/camel-case-switcher/repository/master/archive.tar.gz',
    license='MIT',
    author='USSX Hares / Peter Zaitcev',
    author_email='ussx.hares@yandex.ru',
    description='Python tool for changing style in name of functions etc. from camelCase/CamelCase to the underscore_style.',
    keywords=['camel_case', 'strings', 'undescore_style', 'snake_case'],
)
