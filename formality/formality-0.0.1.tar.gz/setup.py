import setuptools

setuptools.setup(
    name="formality",
    version=open('VERSION').read().strip(),
    url="https://github.com/uchchwhash/formality",

    author="Imam Tashdid ul Alam",
    author_email="imam.alam@gmail.com",

    description="mathematical expression manipulation engine",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)
