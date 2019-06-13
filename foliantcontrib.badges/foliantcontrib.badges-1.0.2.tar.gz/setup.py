from setuptools import setup


SHORT_DESCRIPTION = 'Badges for Foliant.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='foliantcontrib.badges',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='1.0.2',
    author='Daniil Minukhin',
    author_email='ddddsa@gmail.com',
    url='https://github.com/foliant-docs/foliantcontrib.badges',
    packages=['foliant.preprocessors'],
    license='MIT',
    platforms='any',
    install_requires=[
        'foliant>=1.0.8',
        'foliantcontrib.utils.combined_options>=1.0.1',
        'foliantcontrib.utils.preprocessor_ext>=1.0.0'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ]
)
