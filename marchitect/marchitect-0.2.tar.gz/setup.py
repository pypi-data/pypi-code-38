from pathlib import Path
from setuptools import setup

README = (Path(__file__).parent / 'README.md').read_text()

setup(
    name='marchitect',
    version='0.2',
    description='Machine architect for software deployment.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Ken Elkabany',
    author_email='ken@elkabany.com',
    license='MIT',
    url='https://www.github.com/kelkabany/marchitect',
    packages=['marchitect'],
    package_data={'marchitect': ['py.typed']},
    zip_safe=False,
    install_requires=[
        'jinja2>=2.10',
        'ssh2-python>=0.17.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
    ],
)
