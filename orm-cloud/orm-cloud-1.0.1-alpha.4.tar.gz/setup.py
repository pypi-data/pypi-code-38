from setuptools import setup, find_packages, Command

setup(
    name='orm-cloud',
    version='1.0.1-alpha.4',
    description='An ORM solution for serverless cloud platforms',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['ORM', 'cloud', 'serverless'],
    url='https://github.com/gregchagnon/orm.cloud',
    author='Gregory Chagnon',
    author_email='greg@gregchagnon.io',
    license='Apache 2.0',
    packages=find_packages(exclude=(["*.tests", "*.tests.*", "tests.*", "tests"])),
    install_requires=[
        'pymssql'
    ],
    include_package_data=True,
    zip_safe=False
)
