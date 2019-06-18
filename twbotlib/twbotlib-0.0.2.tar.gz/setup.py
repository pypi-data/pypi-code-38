import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='twbotlib',
    version='0.0.2',
    author='truedl',
    author_email='terajamoffical@example.com',
    description='🐦 Unoffical twitch bot library written in Python3 🤖',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/truedl/twbotlib',
    packages=['twbotlib', 'twbotlib.base'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)