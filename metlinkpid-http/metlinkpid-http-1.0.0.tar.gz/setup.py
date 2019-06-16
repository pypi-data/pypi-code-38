from pathlib import Path

import setuptools

README = Path(__file__).parent / 'README.rst'

setuptools.setup(
    name='metlinkpid-http',
    version='1.0.0',
    description='HTTP server for Metlink PID',
    long_description=README.read_text(),
    url='https://github.com/Lx/python-metlinkpid-http',
    author='Alex Peters',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    py_modules=['metlinkpid_http'],
    python_requires='~=3.6',
    install_requires=[
        'metlinkpid~=1.0.1',
        'flask~=1.0.2',
        'envopt~=0.2.0',
        'waitress~=1.3.0',
    ],
    entry_points={
        'console_scripts': [
            'metlinkpid-http=metlinkpid_http:main',
        ],
    },
)
