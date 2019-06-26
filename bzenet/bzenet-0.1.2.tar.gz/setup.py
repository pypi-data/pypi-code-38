from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext

import glob
import sys

_enet_src = glob.glob("enet/*.c")
_enet_inc = glob.glob("enet/include/*/*.h")

if not _enet_src or not _enet_inc:
    print("You need to download and extract the enet 1.3 source to enet/")
    print("Download the source from: http://enet.bespin.org/Downloads.html")
    print("See the README for more instructions")
    sys.exit(1)

source_files = ["enet.pyx"]
source_files.extend(_enet_src)

define_macros = [('HAS_POLL', None),
                 ('HAS_FCNTL', None),
                 ('HAS_MSGHDR_FLAGS', None),
                 ('HAS_SOCKLEN_T', None)]

libraries = []
flags = ["-O3"]

if sys.platform == 'win32':
    define_macros.extend([('WIN32', None)])
    libraries.extend(['ws2_32', 'Winmm'])
    flags = ["/O2"]

if sys.platform != 'darwin':
    define_macros.extend([('HAS_GETHOSTBYNAME_R', None),
                          ('HAS_GETHOSTBYADDR_R', None)])

ext_modules = [
    Extension(
        "bzenet",
        extra_compile_args=flags,
        sources=source_files,
        include_dirs=["enet/include/"],
        libraries=libraries,
        define_macros=define_macros)
    ]

setup(
    name='bzenet',
    version='0.1.2',
    description='A python wrapper for the ENet library ver. 1.3.14',
    url='https://github.com/smile4u/bzenet',
    maintainer='Sergey Zdanevich, BlitzTeam',
    maintainer_email='sergey.zdanevich@blitzteam.com',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    setup_requires=['Cython>=0,<1'],
    install_requires=['Cython>=0,<1']
)
