from strongr.configdomain.model import DefaultsLoader, IniLoader, JsonLoader, YamlLoader

import strongr.core

class LoadConfigHandler():
    def __call__(self, command):
        config_dict = DefaultsLoader().getConfig()
        strongr.core.getCore().config.update(ConfigStruct(**config_dict))

        loaders = {
            IniLoader.__name__: IniLoader(),
            JsonLoader.__name__: JsonLoader(),
            YamlLoader.__name__: YamlLoader()
        }

        loadOrder = ConfigStruct(**config_dict).internal.configloaderorder
        for loaderName in loadOrder:
            if loaderName in loaders:
                config_dict = self._deep_update(config_dict, loaders[loaderName].getConfig(command.environment))
                # update config in core many times as config loaders can use config parameters from other loaders
                # example: a database configloader that needs credentials
                strongr.core.getCore().config.update(ConfigStruct(**config_dict))
            else:
                # fatal error
                # since the loadOrder is hardcoded in the defaultsloader it should always work. If not,
                # it is considered a fatal error.
                raise Exception("Invalid config loader!")

    def _deep_update(self, dict_left, dict_right):
        for key, value in dict_right.items():
            if isinstance(value, dict):
                result = self._deep_update(dict_left.get(key, {}), value)
                dict_left[key] = result
            else:
                dict_left[key] = dict_right[key]
        return dict_left


class ConfigStruct(object):
    def __init__(self, **entries):
        for key in entries:
            if isinstance(entries[key], dict):
                entries[key] = ConfigStruct(**entries[key])
        self.__dict__.update(entries)

    def as_dict(self):
        output = self.__dict__
        for key in output:
            if isinstance(output[key], ConfigStruct):
                output[key] = output[key].as_dict()
        return output
