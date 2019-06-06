from setuptools import setup, find_packages

setup(
    name='unv.deploy',
    version='0.3.7',
    description="""Deploy helpers for UNV framework""",
    url='http://github.com/c137digital/unv_deploy',
    author='Morty Space',
    author_email='morty.space@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        'unv.app',
        'unv.utils',
        'jinja2',
        'watchgod'
    ],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'deploy = unv.deploy.bin:run'
        ]
    }
)
