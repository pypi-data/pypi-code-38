from setuptools import find_packages, setup


version_info = {}
with open('grpc_wrappers/_version.py') as version_file:
    exec(version_file.read(), version_info)


setup(
    name='grpc_wrappers',
    version=version_info['__version__'],
    versioning='post',
    author=version_info['__author__'],
    author_email=version_info['__author_email__'],
    url='https://github.com/matthewwardrop/python-grpc-wrappers',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    setup_requires=['setupmeta'],
    install_requires=[
        'arrow',
        'grpcio',
        'interface_meta',
        'protobuf',
    ]
)
