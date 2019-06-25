from setuptools import setup

with open('README.md', 'r') as fp:
    long_description = fp.read()


setup(
    name='is_disposable_email',
    version='1.0.0',
    author='Akhil Harihar',
    author_email="hariharakhil@gmail.com",
    description='Check if the email address is from a disposable email service \
        provider',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akhilharihar/is_disposable_email",
    packages=['is_disposable_email'],
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        'Development Status :: 5 - Production/Stable'
    ]
)
