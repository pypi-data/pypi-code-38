from setuptools import setup

setup(
    name='helpdeskbot',
    version='1.6.1',
    description='Discord utility bot for DevDungeon.com',
    url='https://github.com/DevDungeon/HelpDeskBot',
    author='DevDungeon',
    author_email='nanodano@devdungeon.com',
    license='GPL-3.0',
    packages=['helpdeskbot'],
    scripts=[
        'bin/helpdeskbot',
        'bin/helpdeskbot.bat',
    ],
    zip_safe=False,
    python_requires='<3.7',
    install_requires=[
        'discord.py==0.16.12',
        'docopt',
        'aiohttp',
    ]
)
