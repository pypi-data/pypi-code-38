from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='funf',
    version='0.1.1',
    description='Useful tools and functions in Python',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Ashvini Jangid',
    author_email='ashvinijangid@gmail.com',
    keywords=['func', 'Gcd', 'funcs'],
    # url='https://github.com/ncthuc/elastictools',
    # download_url='https://pypi.org/project/elastictools/'
)

install_requires = []

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
