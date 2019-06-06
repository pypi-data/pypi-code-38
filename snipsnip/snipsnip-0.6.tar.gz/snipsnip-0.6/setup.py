from setuptools import setup

setup(
    name='snipsnip',
    version='0.6',
    description='Remote mac clipboard',
    url='http://github.com/AGhost-7/snipsnip',
    author='Jonathan Boudreau',
    author_email='jonathan.boudreau.92@gmail.com',
    license='MIT',
    keywords=['clipboard'],
    zip_safe=False,
    install_requires=[
        'pyperclip >= 1.7.0',
        'python-xlib >= 0.25;platform_system=="Linux"'
    ],
    entry_points={
        'console_scripts': ['snipsnip=snipsnip:main']
    },
)
