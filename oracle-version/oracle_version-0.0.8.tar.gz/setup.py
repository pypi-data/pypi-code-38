from distutils.core import setup

setup(
    name='oracle_version',  # How you named your package folder (MyLib)
    packages=['oracle'],  # Chose the same as "name"
    version='0.0.8',  # Start with a small number and increase it with every change you make
    license='BSD 4',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Oracle is version name generator with version journal this ensures that version names are unique.',
    # Give a short description about your library
    author='Egnod',  # Type in your name
    author_email='egnod@yandex.ru',  # Type in your E-Mail
    url='https://github.com/Egnod/oracle',  # Provide either the link to your github or to your website
    download_url='https://github.com/Egnod/oracle/archive/master.zip',  # I explain this later on
    keywords=['Versions', 'Generators', 'Oracle', "Version Generator", "Version Name generator"],
    # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'emoji',
        'requests'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
    ],
)
