from setuptools import setup, Extension

bell_yespower_module = Extension('bell_yespower',
                            sources = ['yespower-module.c',
                                       'yespower.c',
                                       'yespower-opt.c',
                                       'sha256.c'
                                       ],
                            extra_compile_args=['-O2', '-funroll-loops', '-fomit-frame-pointer'],
                            include_dirs=['.'])

setup (name = 'bell_yespower',
       version = '1.0.3',
       author_email = 'yuto_tetuota@yahoo.co.jp',
       author = 'y-chan',
       url = 'https://github.com/bellcoin-electrum/bell_yespower_python3',
       description = 'Bindings for yespower-1.0 proof of work used by bellcoin',
       ext_modules = [bell_yespower_module])
