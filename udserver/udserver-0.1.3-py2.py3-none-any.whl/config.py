import pkg_resources

# if getattr(sys, 'frozen', False):
#     currentpath = os.path.dirname(os.path.realpath(sys.executable))
# elif __file__:
#     currentpath = os.path.dirname(os.path.realpath(__file__))

package_name = 'udserver'


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    STORAGE_FOLDER = pkg_resources.resource_filename(package_name, 'storage')
    LOG_FILE = pkg_resources.resource_filename(package_name, 'ud_server.log')


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
