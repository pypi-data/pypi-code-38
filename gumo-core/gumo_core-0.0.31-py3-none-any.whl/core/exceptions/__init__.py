class GumoBaseError(RuntimeError):
    pass


class ConfigurationError(GumoBaseError):
    pass


class ServiceAccountConfigurationError(ConfigurationError):
    pass


class ObjectNotoFoundError(GumoBaseError):
    pass
