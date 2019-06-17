from distutils.core import setup
import glob

mods = glob.glob("*.py") + glob.glob("gallery_plugins/*.py") # not using recursive "**", unsupported in Python 2
mods.remove("setup.py")
setup(name = 'gallery_get',
    version = '1.8.6',
    author = 'Rego Sen',
    author_email = 'regosen@gmail.com',
    url = 'https://github.com/regosen/gallery_get',
    description = 'Gallery downloader - supports many galleries and reddit user histories',
    long_description = open("README.rst","r").read(),
    license = 'MIT',
    keywords = 'gallery downloader reddit imgur imgbox 4chan xhamster eroshare vidble pornhub xvideos imagebam',
    py_modules = [x.replace(".py","") for x in mods],
    packages=['gallery_plugins'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Multimedia :: Graphics',
    ],
)