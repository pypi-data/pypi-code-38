from setuptools import setup

setup(
    name='fasthaversine',
    version='0.1.2',
    description='A fast vectorized version of haversine distance calculation.',
    include_package_data=True,
    install_requires=['numpy'],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Qiyu Liu',
    author_email='keiyuk.liu@gmail.com',
    maintainer='Qiyu Liu',
    maintainer_email='keiyuk.liu@gmail.com',
    url='https://github.com/qyliu-hkust/fasthaversine',
    download_url='https://github.com/qyliu-hkust/fasthaversine/archive/0.1.2.tar.gz',
    packages=['fasthaversine'],
    license=['MIT'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Mathematics'
    ],
)
