import setuptools

setuptools.setup(
    name="mtrx",
    version="0.1.5",
    author="Mostafa Vahedi Nejad",
    author_email="mostafa.vahedi.nejad@gmail.com",
    description="A Python ToolBox",
    long_description=open('README').read(),
    long_description_content_type="text/markdown",
    url="https://mtrx.ir",
    download_url='https://github.com/mostafa-vn/mtrx.git',
    packages=setuptools.find_packages(),
    keywords="mtrx mostafa matrix python v3",
    install_requires=['requests', 'pyqrcode', 'dnspython', 'autopy'],
    license='MIT',
    platforms=['any'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
    	'Environment :: Console',
    	'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
