PACKAGERS = APT, YUM = ('apt-get', 'yum')

APT_KEY = 'apt-key'
APT_SOURCE = 'apt-source'

OS_TYPES = LINUX, WINDOWS = ('linux', 'windows')
OS_DISTRO = (
    FEDORA,
    UBUNTU,
    DEBIAN,
    RASPBIAN,
    CENTOS,
    SUNOS,
    ARCH,
    REDHAT,
    SLES,
    GENTOO,
) = (
    'fedora',
    'ubuntu',
    'debian',
    'raspbian',
    'centos',
    'sunos',
    'arch',
    'redhat',
    'sles',
    'gentoo',
)

SUN = 'sun'

WHEEZY = 'wheezy'
JESSIE = 'jessie'

SYSTEM = 'system'
RUBY = 'ruby'
PYTHON = 'python'
PACKAGE_TYPES = (
    SYSTEM,
    PYTHON, # pip
    RUBY, # gem
)

ALL = 'all' # denotes the global role

START = 'start'
STOP = 'stop'
STATUS = 'status'
RELOAD = 'reload'
RESTART = 'restart'
ENABLE = 'enable'
DISABLE = 'disable'
STATUS = 'status'
SERVICE_COMMANDS = (
    START,
    STOP,
    STATUS,
    RESTART,
    ENABLE,
    DISABLE,
    STATUS,
)

DJANGO = 'DJANGO'

SITE = 'SITE'
ROLE = 'ROLE'

LOCALHOST_NAME = 'localhost'
LOCALHOST_IP = '127.0.0.1'
LOCALHOSTS = (LOCALHOST_NAME, LOCALHOST_IP)

UTF8 = 'UTF8'

STORAGE_LOCAL = 'local'
STORAGE_REMOTE = 'remote'
STORAGES = (
    STORAGE_LOCAL,
    STORAGE_REMOTE,
)

LOCALHOSTS = ('localhost', '127.0.0.1')

LOCAL_VERBOSE = 1
GLOBAL_VERBOSE = 2
