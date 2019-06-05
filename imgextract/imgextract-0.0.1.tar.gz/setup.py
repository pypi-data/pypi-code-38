import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name="imgextract",
    version="0.0.1",
    scripts=['imgextract/imgext.py', 'imgextract/imggui.py'],
    author="Sai Kumar Yava",
    author_email="saikumar.geek@gmail.com",
    description="A python package for extracting images from PDF/TIF files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/scionoftech/imgextract",
    download_url="https://github.com/scionoftech/imgextract/releases/tag/imgextract_stable_v0.0.1",
    install_requires=['pdf2image', 'scikit-image', 'Pillow'],
    packages=['imgextract'],
    package_data={'': ['proppler/*']},
    include_package_data=True,
    keywords=['pdf', 'tif', 'tiff', 'image'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',

    ],

)
# packages=setuptools.find_packages(include=['lib', 'lib.*', 'frames']),
# package_data = {'': ['*.py', 'lib/*']},
# include_package_data = True,
# data_files = [('lib/*')],
