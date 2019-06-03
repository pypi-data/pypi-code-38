__version__ = '0.0.1'
__name__ = 'nerdvision'
agent_name = 'NerdVision Python Agent'

__version_major__ = '0'
__version_minor__ = '0'
__version_micro__ = '1'

__props__ = {
    '__Git_Branch__': '',
    '__Git_Commit_Id__': '',
    '__Git_Commit_Time__': '2019-05-31 14:58:01+02:00',
    '__Git_Dirty__': 'True',
    '__Git_Remote_Origin_Url__': 'git@gitlab.com:intergral/agents/python-client.git',
    '__Git_Tags__': '[]',

    '__X_CI_Pipeline_Id__': '',
    '__X_CI_Pipeline_Iid__': '',
    '__X_CI_Pipeline_Source__': '',
    '__X_CI_Pipeline_Url__': '',
    '__X_CI_Project_Name__': '',
}


def start(api_key, name=None, tags=None, agent_settings=None):
    from nerd_vision.NerdVision import NerdVision

    agent_settings['name'] = name
    agent_settings['api_key'] = api_key
    agent_settings['tags'] = tags

    from nerd_vision import settings
    settings.configure_agent(agent_settings)

    api_key = settings.get_setting("api_key")
    if api_key is None:
        configure_logger().error("Stream hippo api key is not defined.")
        exit(314)

    hippo = NerdVision()
    hippo.start()
    return hippo


def configure_logger():
    from nerd_vision import settings
    import logging
    from logging.handlers import SysLogHandler

    log_file = settings.get_setting("log_file")
    level = settings.get_setting("log_level")

    file_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10000000, backupCount=5, encoding=None,
                                                        delay=0)
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s NerdVision: [%(levelname)s] %(message)s', datefmt='%b %d %H:%M:%S')

    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    our_logger = logging.getLogger("nerdvision")
    our_logger.propagate = False
    our_logger.setLevel(level)

    our_logger.addHandler(file_handler)
    our_logger.addHandler(stream_handler)

    return our_logger
