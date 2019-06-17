from setuptools import setup, Extension

zny_yespower_0_5_module = Extension('zny_yespower_0_5',
                            sources = ['yespower-module.c',
                                       'yespower.c',
                                       'yespower-opt.c',
                                       'sha256.c'
                                       ],
                            extra_compile_args=['-O2', '-funroll-loops', '-fomit-frame-pointer'],
                            include_dirs=['.'])

setup (name = 'zny_yespower_0_5',
       version = '1.0.2',
       author_email = 'yuto_tetuota@yahoo.co.jp',
       author = 'y-chan',
       url = 'https://github.com/bitzeny-electrum/zny_yespower_0_5_python3',
       description = 'Bindings for yespower-0.5 proof of work used by bitzeny',
       ext_modules = [zny_yespower_0_5_module])
