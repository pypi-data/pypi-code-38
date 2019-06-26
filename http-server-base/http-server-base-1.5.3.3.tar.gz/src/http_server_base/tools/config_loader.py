import json
from logging import getLogger
from functools import reduce
from typing import Union, Dict, List, Any, Callable

import os
from http_server_base.tools import JsonSerializable

logger = getLogger('http_server.tools.config_loader')


class ConfigLoader:
    __active_configs: Dict[str, JsonSerializable] = {}
    __config_locations: Dict[str, str] = {}
    __main_config_key: str = 'main'
    __main_config_path: str = 'configs/server.json'
    
    __DEFAULT_OBJECT = object()
    __MAIN_CONFIG_NOT_FOUND_EXIT_CODE: int = 3
    
    #region Private methods
    @staticmethod
    def __load_main_config(main_config_path:str, soft_mode:bool):
        logger.info("Loading main configuration")
        if (main_config_path):
            logger.debug(f"Overriding default config path: {main_config_path}")
            ConfigLoader.__main_config_path = main_config_path
        
        logger.info("Config is used: {configPath}".format(configPath=os.path.abspath(ConfigLoader.__main_config_path)))

        main_config = ConfigLoader.__try_load(ConfigLoader.__main_config_path)
        if (main_config is ConfigLoader.__DEFAULT_OBJECT):
            if (soft_mode):
                logger.warning("Config loader is initialized in the soft mode. Skipping the main configuration")
                ConfigLoader.__store_config(key=ConfigLoader.__main_config_key, path=None, config=dict())
            else:
                logger.critical("Critical error. Cannot read configuration file. Exiting now.")
                exit(ConfigLoader.__MAIN_CONFIG_NOT_FOUND_EXIT_CODE)
        else:
            ConfigLoader.__store_config(key=ConfigLoader.__main_config_key, path=ConfigLoader.__main_config_path, config=main_config)
            logger.debug("Main config loaded successfully")
    
    @staticmethod
    def __store_config(key:str, config:dict, path:str=None):
        if (key in ConfigLoader.__active_configs):
            del ConfigLoader.__active_configs[key]
        ConfigLoader.__active_configs[key] = config
        
        if (not path is None):
            if (key in ConfigLoader.__config_locations):
                del ConfigLoader.__config_locations[key]
            ConfigLoader.__config_locations[key] = path
    
    @staticmethod
    def __expand_config(obj: Dict[str, Any]):
        for key in list(obj.keys()):
            x = obj[key]
            if (isinstance(x, dict)):
                ConfigLoader.__expand_config(x)
                for x_key in x:
                    obj[f"{key}/{x_key}"] = x[x_key]
        
    @staticmethod
    def __try_load(path:str) -> Union[Dict[str, Any], object]:
        try:
            logger.debug(f"Trying to load configuration: {path}")
        
            config_file = open(path)
            config = json.load(config_file)
            ConfigLoader.__expand_config(config)
            
            logger.debug("Config loaded successfully")
            logger.debug(json.dumps(config, indent=4, sort_keys=True))
    
        except FileNotFoundError:
            logger.error("Error while loading configuration: File not found.")
            result = ConfigLoader.__DEFAULT_OBJECT
        except json.JSONDecodeError:
            logger.error("Error while loading configuration: File is not JSON-serializable.")
            result = ConfigLoader.__DEFAULT_OBJECT
        except:
            logger.exception("Unhandled error while loading configuration:")
            result = ConfigLoader.__DEFAULT_OBJECT
        else:
            config_file.close()
            result = config
        
        return result
    #endregion
    
    #region Public methods
    @staticmethod
    def load_config(key:str, path:str) -> bool:
        """
        Loads a config with the given name & given path.
        Called by load_configs method.
        
        :param key:
        str key / name of the config to be loaded.
        :param path:
        str path (full or relative) to the configuration file.
        :return:
        Returns True if config was loaded successfully.
        Returns False otherwise.
        """
        
        config = ConfigLoader.__try_load(path)
        if (config is ConfigLoader.__DEFAULT_OBJECT):
            return False
        
        ConfigLoader.__store_config(key=key, path=path, config=config)
        logger.debug(f"Config '{key}' loaded successfully")
        return True

    @staticmethod
    def load_configs(main_config_path: str = None, config_paths: Union[None, List[str], Dict[str, str], str] = None, soft_mode: bool = False):
        """
        Loads configuration from the config files given. All files should be in the JSON-format.

        :param main_config_path:
        str path to the main configuration file. By default, 'configs/server.json' is used.
        Exits the program with the critical error in log and exit code 3 if config is not found.
        :param config_paths:
        Names or paths to the additional configs. The following combinations are allowed:
          - None: additional configs will not be loaded
          - List[str]: a list of names of configs. Scans the main config for the 'configDirectory' value and the '{config_name}Config' value; then loads appropriate configs.
          - Dict[str, str]: a dict object of config names and config paths. Loads the config of given paths.
        Does not raises any exceptions if config is not found.
        :param soft_mode:
        bool flag that describes will application fail if the main config is not found or not.
        True - will not fail; False - will fail. Default - False.
        :return:
        :exception ValueError:
        ValueError is raised if config_paths argument is configured wrongly.
        """
        
        error = False
        ConfigLoader.__load_main_config(main_config_path, soft_mode=soft_mode)
        if (config_paths is None):
            pass
        elif (isinstance(config_paths, list)):
            config_dir = ConfigLoader.get_from_config('configDirectory', default='')
            for _config_name in config_paths:
                ConfigLoader.load_config(_config_name, config_dir + ConfigLoader.get_from_config(f'{_config_name}Config'))
        elif (isinstance(config_paths, dict)):
            for _config_name in config_paths:
                ConfigLoader.load_config(_config_name, config_paths[_config_name])
        elif (isinstance(config_paths, str)):
            config_paths = config_paths.lower()
            if (config_paths == "default"):
                config_dir = ConfigLoader.get_from_config('configDirectory', default='')
                for key, value in ConfigLoader.__active_configs[ConfigLoader.__main_config_key].items():
                    if (not '/' in key and key.endswith('Config')):
                        _config_name, _, _ = key.rpartition('Config')
                        ConfigLoader.load_config(_config_name, config_dir + value)
            else:
                error = True
        else:
            error = True
        
        if (error):
            raise ValueError(f"config_paths argument: got: {type(config_paths)}; expected: either List[str], Dict[str,str], None or str: 'default'")

    @staticmethod
    def reload_config(config_name:str) -> bool:
        """
        Tries to reload a single config with the given name. If failed, uses the old stored value.
        
        :param config_name:
        str key / name of config to be reloaded.
        :return:
        Returns True if config was reloaded successfully.
        Returns False otherwise.
        """
        
        if (config_name in ConfigLoader.__config_locations):
            new_config = ConfigLoader.__try_load(ConfigLoader.__config_locations[config_name])
            if (new_config is ConfigLoader.__DEFAULT_OBJECT):
                logger.error("Reloading configuration unsuccessful, restoring old config.")
                return False
            
            ConfigLoader.__store_config(key=config_name, config=new_config)
            logger.info(f"Configuration '{config_name}' reloaded successfully.")
            return True
        
        logger.error("Reloading configuration unsuccessful - nothing to reload.")
        return False
    
    @staticmethod
    def reload_configs() -> bool:
        """
        
        Tries to reload all loaded configs, including main.
        If any fails, restores all old values.
        :return:
        Returns True if all configs were reloaded successfully.
        Returns False otherwise.
        """
        
        new_configs = None
        for config_name in ConfigLoader.__active_configs:
            _cfg = ConfigLoader.__try_load(ConfigLoader.__config_locations[config_name])
            if (_cfg is ConfigLoader.__DEFAULT_OBJECT):
                logger.error("Reloading configuration unsuccessful, restoring old configs.")
                return False
            
            if (new_configs is None):
                new_configs = dict()
            new_configs[config_name] = _cfg
        
        for config_name in ConfigLoader.__active_configs:
            ConfigLoader.__store_config(key=config_name, config=new_configs[config_name])
        
        if (new_configs is None):
            logger.error("Reloading configuration unsuccessful - nothing to reload.")
            return False
        
        del new_configs
        logger.info("All configuration reloaded successfully.")
        return True
        
    @staticmethod
    def get_from_config(path:str, config_name:str='main', default:Union[Any, Callable[[], Any]]=None) -> Any:
        """
        Returns value of the preloaded config by its path.
        
        :param path:
        Path in the configuration file, separated by '/'
        :param config_name:
        Name of preloaded config. If missing, searches value in the main config.
        :param default:
        Returns this value if either path was not found in config or config of given name was not found.
        This value supports lazy argument passing. To do so, send an callable with no arguments.
        :return:
        Returns the value found, or the default value, or None
        """
        
        result = ConfigLoader.__DEFAULT_OBJECT
        if (config_name in ConfigLoader.__active_configs):
            result = ConfigLoader.__active_configs[config_name].get(path, ConfigLoader.__DEFAULT_OBJECT)
        
        if (result is ConfigLoader.__DEFAULT_OBJECT):
            if (callable(default)):
                return default()
            return default
        
        return result
    #endregion
