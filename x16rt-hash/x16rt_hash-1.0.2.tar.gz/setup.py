from distutils.core import setup, Extension

with open("README.md", "r") as fh:
       long_description = fh.read()

x16rt_hash_module = Extension('x16rt_hash',
                               sources = ['x16rtmodule.c',
                                          'x16rthash.c',
                                          'sha3/blake.c',
                                          'sha3/bmw.c',
                                          'sha3/groestl.c',
                                          'sha3/jh.c',
                                          'sha3/keccak.c',
                                          'sha3/skein.c',
                                          'sha3/cubehash.c',
                                          'sha3/echo.c',
                                          'sha3/luffa.c',
                                          'sha3/sha2.c',
                                          'sha3/simd.c',
                                          'sha3/hamsi.c',
                                          'sha3/hamsi_helper.c',
                                          'sha3/fugue.c',
                                          'sha3/shavite.c',
                                          'sha3/shabal.c',
                                          'sha3/whirlpool.c',
                                          'sha3/sha2big.c'],
                            include_dirs=['.', './sha3'])

setup (name = 'x16rt_hash',
       version = '1.0.2',
       author = 'random.zebra',
       author_email = '',
       description = 'Bindings for X16RT hashing PoW',
       long_description=long_description,
       long_description_content_type="text/markdown",
       url='https://github.com/random-zebra/x16rt_hash',
       ext_modules = [x16rt_hash_module])
