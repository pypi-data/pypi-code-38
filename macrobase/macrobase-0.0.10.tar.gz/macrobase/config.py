from macrobase_driver.config import SimpleConfig, LogLevel, LogFormat


class SimpleAppConfig(SimpleConfig):

    LOGO: str = """
                                    _                    
                                   | |                   
     _ __ ___   __ _  ___ _ __ ___ | |__   __ _ ___  ___ 
    | '_ ` _ \ / _` |/ __| '__/ _ \| '_ \ / _` / __|/ _ \\
    | | | | | | (_| | (__| | | (_) | |_) | (_| \__ \  __/
    |_| |_| |_|\__,_|\___|_|  \___/|_.__/ \__,_|___/\___|
"""

    VERSION: str = '0.0'
    NAME: str = 'macrobase'
    DEBUG: bool = False
    WORKERS: int = 1

    LOG_FORMAT: LogFormat = LogFormat.json
    LOG_LEVEL: LogLevel = LogLevel.info


class AppConfig(SimpleAppConfig):
    """
    Application config
    """

    pass
