import os

VALID_SECTIONS = [
    'default', 'development', 'test', 'homolog', 'staging', 'production'
]


class SettingsMeta(type):
    def __new__(meta, name, bases, attrs):

        if name == 'DefaultSettings':
            return super().__new__(meta, name, bases, attrs)

        _declared_options = {}

        base_options = meta.fetch_base_options(bases)

        # subclass declared options
        _explicit_options = {
            key: value
            for key, value in attrs.items() if key.isupper()
        }

        _declared_options.update(base_options)

        _declared_options.update(_explicit_options)

        API_ENV = _declared_options.get('API_ENV')

        # only allow debug model in development & test environment
        is_debug = attrs.get('DEBUG', False) and (API_ENV in ['development', 'test'])

        base_dir = attrs.get('BASE_DIR')
        config_files = attrs.get('_config_files', [])

        if config_files and not base_dir:
            raise Warning(
                f'Please put this line: "BASE_DIR = os.path.dirname(os.path.abspath(__file__))" into your setting class: "{name}"'
            )

        # Subclass config files  has higher priority
        config_files = list(map(lambda x: os.path.sep.join([base_dir, x]), config_files))

        if is_debug:
            print(f'\n{name}:{config_files}\n')

        # configuration options from configuration files
        file_options = meta.load_config_from_files(API_ENV, config_files)

        # build current class's all declared configuration options including all superclass
        # base_options.update(attrs)

        # override class's declared options with file configuration with validation also
        for key, value in file_options.items():
            if is_debug:
                print(f'\nfile options: {key} = {value}\n')
            setting_key = key.upper()
            if setting_key not in _declared_options:
                raise Warning(f'Configuration field "{key}" should be declared in "{name}" class')

            if value.startswith('$'):
                value = os.environ.get(value[1:], None)

            if value is not None:
                if value.isnumeric():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

            _explicit_options[setting_key] = value

        # setting manager's extra configuration settings which have the highest priority that override all previous settings
        setting_managers = attrs.get('_setting_managers', [])
        for key, value in meta.load_config_from_plugins(
                API_ENV, setting_managers).items():
            setting_key = key.upper()
            if setting_key not in _declared_options:
                raise Warning(f'Configuration field:"{setting_key}" should be declared in "{name}" class!')
            _explicit_options[setting_key] = value

        _declared_options.update(_explicit_options)

        # If subclass overload superclass's attribute, update super class
        for key, value in _declared_options.items():
            if not key.isupper():
                continue
            for base in bases:
                setattr(base, key, value)

        if is_debug: 
            print(f'\n{name} : {_declared_options}\n')
        attrs.update(_declared_options)

        return super(SettingsMeta, meta).__new__(meta, name, bases, attrs)

    @classmethod
    def is_overload(cls, setting: str = None, base_settings: dict = None):
        return setting in base_settings

    @classmethod
    def fetch_base_options(cls, bases):
        base_config_attributes = {}
        for base in bases:
            base_config_attributes.update({
                key: value
                for key, value in base.__dict__.items() if key.isupper()
            })
        return base_config_attributes

    @classmethod
    def load_config_from_plugins(cls, api_env: str, plugins: list) -> dict:
        """
        Loading config options from plugin classes  
        """
        import inspect
        manager_settings = {}
        for plugin in plugins:
            if inspect.isclass(plugin) and issubclass(plugin, SettingManager):
                obj = plugin(api_env=api_env)
            elif isinstance(plugin, SettingManager):
                obj = plugin
                obj.api_env = api_env
            else:
                raise Warning(
                    f'plugin:{plugin} should be an instance or subclass of SettingManager'
                )
            manager_settings.update(obj())
        return manager_settings

    @classmethod
    def load_config_from_files(cls, env_name, files) -> dict:
        from configparser import ConfigParser
        global_config = {}
        config = ConfigParser()
        for filename in files:
            if not os.path.exists(filename):
                raise Warning(
                    'Can not found config file: "{}"'.format(filename))
            config.read(filename)
            for section in config.sections():
                if section not in VALID_SECTIONS:
                    raise Exception('Invalid section {} in  {}'.format(
                        section, filename))

            default_section = dict(config.items(
                'default')) if config.has_section('default') else {}
            env_name_section = dict(config.items(
                env_name)) if config.has_section(env_name) else {}
            global_config.update(default_section)
            global_config.update(env_name_section)
        return global_config


class SettingManager:
    """
    Base class of Setting plugin  which has the highest priority than attribute and config file 
    """

    # allow configuration option value be None
    ALLOW_NONE_VALUE = False

    DEFAULT = {}
    DEVELOPMENT = {}
    TEST = {}
    HOMOLOG = {}
    STAGING = {}
    PRODUCTION = {}

    def __init__(self, api_env='development'):
        self.api_env = api_env

    def default_settings(self) -> dict:
        return self.DEFAULT

    def development_settings(self) -> dict:
        return self.DEVELOPMENT

    def test_settings(self) -> dict:
        return self.TEST

    def homolog_settings(self) -> dict:
        return self.HOMOLOG

    def staging_settings(self) -> dict:
        return self.STAGING

    def production_settings(self) -> dict:
        return self.PRODUCTION

    def __call__(self) -> dict:
        """
        SettingsMeta call this method to load settings from plugin class 
        """

        self._default_config = self.default_settings()
        self._default_config.update(
            getattr(self, f'{self.api_env}_settings')())
        return {
            key: value
            for key, value in self._default_config.items()
            if self.ALLOW_NONE_VALUE or (not self.ALLOW_NONE_VALUE and value)
        }


class DefaultSettings(metaclass=SettingsMeta):
    """
    Default project global scope
    """
    # load configuration options from ini file
    _config_files = []

    # load configuration options from any SettingManager plugins
    _setting_managers = []

    API_ENV = os.environ.get('API_ENV', 'development')
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # API return data related configuration
    API_DEFAULT_LIMIT = 20
    API_MAXIMUM_LIMIT = 100

    DEBUG = True

    ############################################################
    # Mongo Database configuration template
    ############################################################
    MONGODB_URI = None
    DB_NAME = 'default_db'
    COLLECTION_NAME = 'default'

    @classmethod
    def mongo_config_for_collection(cls, collection_name: str = None):
        """
        Return a configuration object of MongoDBManager for given collection_name
        If collection_name in any configuration file then use the configured collection_name
        Else use the given collection_name instead
        """
        if collection_name is None:
            collection_name = cls.COLLECTION_NAME

        if not getattr(cls, collection_name, False):
            collection_name = collection_name
        else:
            collection_name = getattr(cls, collection_name)
        return {
            'MONGODB_URI': cls.MONGODB_URI,
            'DB_NAME': cls.DB_NAME,
            'COLLECTION_NAME': collection_name
        }

    ############################################################
    # AWS service configuration
    ############################################################
    AWS_REGION = 'us-west-2'
    BUCKET_NAME = None
    AWS_S3_EXPIRATION = 60 * 60 * 24

    @classmethod
    def aws_config(cls):
        """
        Return aws's configuration from environment variable 'API_ENV'
        """
        return {'AWS_REGION': cls.AWS_REGION, 'BUCKET_NAME': cls.BUCKET_NAME}
