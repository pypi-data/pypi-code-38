import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='twbotlib',
    version='0.0.1',
    author='truedl',
    packages=['twbotlib', 'twbotlib.base'],
    author_email='terajamoffical@example.com',
    description='🐦 Unoffical twitch bot library written in Python3 🤖',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/truedl/twbotlib',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)