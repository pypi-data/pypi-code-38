
SETUP_INFO = dict(
    name = 'infi.storagemodel',
    version = '0.4.29',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.storagemodel',
    license = 'BSD',
    description = """A high-level library for traversing the OS storage model.""",
    long_description = """A high-level cross-platform abstraction of the OS storage stack (LUNs, disks, volumes, etc).""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'infi.asi',
'infi.blocking',
'infi.cwrap',
'infi.devicemanager',
'infi.diskmanagement',
'infi.dtypes.hctl',
'infi.dtypes.iqn',
'infi.dtypes.wwn',
'infi.exceptools',
'infi.hbaapi',
'infi.instruct',
'infi.iscsiapi',
'infi.mount-utils',
'infi.multipathtools',
'infi.os-info',
'infi.parted',
'infi.pyutils',
'infi.sgutils',
'infi.traceback',
'infi.wioctl',
'infi.wmpio',
'setuptools',
'six'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['devlist = infi.storagemodel.examples:devlist', 'rescan_scsi_bus = infi.storagemodel.linux.rescan_scsi_bus:console_script'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()
