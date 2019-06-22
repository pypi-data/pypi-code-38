from setuptools import setup, find_packages

with open("README.md", 'r', encoding="utf-8")as file:
    value = file.read()

setup(name="ArknightsPaintingExtract",
      version='1.2.1',
      description='an tool to work with arknights Texture2D',
      url='https://github.com/Goodjooy/ArknightsPaintingExtract',
      author='Jacky_Qing',
      author_email='Jacky_QXNJ@163.com',
      license="""MIT""",
      packages=find_packages(),
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Natural Language :: Chinese (Simplified)",
          "Operating System :: OS Independent",
          'License :: OSI Approved :: MIT License',

          "Programming Language :: Python :: 3.7",
          "Topic :: Desktop Environment :: Window Managers",

      ],
      python_requires='~=3.7',
      long_description=value,
      long_description_content_type="text/markdown",
      install_requires=["wxPython", "Pillow"]
      )
