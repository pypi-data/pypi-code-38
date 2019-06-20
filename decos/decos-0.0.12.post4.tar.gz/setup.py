import setuptools

with open("README.md" ,'r') as f:
    long_description = f.read()

setuptools.setup(
        name='decos',
        version='0.0.12post4',
        author='Vikas Sangwan',
        author_email='16vikas96@gmail.com',
        description='some decorators',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/shang-vikas/decos',
        packages=setuptools.find_packages(),
        classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent"
            ],
        
        )
