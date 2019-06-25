from setuptools import setup, Extension

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='PycHuffman',
    version='1.1.0',
    author='QiaoPeng',
    author_email='john_04047210@163.com',
    license='MIT License',
    description='compress or decompress with huffman',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/john04047210/pyhuffman.git',
    project_urls={
        'Source': 'https://github.com/john04047210/pyhuffman.git',
    },
    ext_modules=[
        Extension('PycHuffman', ['huffman.c','huffmanWrapper.c'], include_dirs=['./'])
    ],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
