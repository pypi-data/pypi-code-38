import setuptools

setuptools.setup(name='goza',
                 version='0.0.7',
                 author="Zach Gongaware",
                 description='You personal Python assistant',
                 packages=setuptools.find_packages(),
                 install_requires=["matplotlib"],
                 classifiers=[
                       "Programming Language :: Python :: 3",
                       "License :: OSI Approved :: MIT License",
                       "Operating System :: OS Independent",
                 ],
                 zip_safe=False)
