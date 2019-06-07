import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="image_classification",
    version="0.1.0",
    author="Sanchit Tanwar",
    author_email="sanchittanwar75@gmail.com",
    description="Image classification in pytorch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanchit2843/image_classification",
    download_url = 'https://github.com/sanchit2843/image_classification/archive/0.1.0.tar.gz',
    install_requires=[            
          'efficientnet_pytorch',
          'torch',
          'torchvision',
          'sklearn'
      ],
            
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 