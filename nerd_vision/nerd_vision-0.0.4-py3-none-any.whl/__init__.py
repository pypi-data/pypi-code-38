__version__ = '${version}'
__name__ = '${name}'
agent_name = '${agent_name}'

__version_major__ = '${version_major}'
__version_minor__ = '${version_minor}'
__version_micro__ = '${version_micro}'

__props__ = {
    '__Git_Branch__': '${Git_Branch}',
    '__Git_Commit_Id__': '${Git_Commit_Id}',
    '__Git_Commit_Time__': '${Git_Commit_Time}',
    '__Git_Dirty__': '${Git_Dirty}',
    '__Git_Remote_Origin_Url__': '${Git_Remote_Origin_Url}',
    '__Git_Tags__': '${Git_Tags}',

    '__X_CI_Pipeline_Id__': '${X_CI_Pipeline_Id}',
    '__X_CI_Pipeline_Iid__': '${X_CI_Pipeline_Iid}',
    '__X_CI_Pipeline_Source__': '${X_CI_Pipeline_Source}',
    '__X_CI_Pipeline_Url__': '${X_CI_Pipeline_Url}',
    '__X_CI_Project_Name__': '${X_CI_Project_Name}',
}


def start(api_key, name=None, tags=None, agent_settings=None):
    from nerdvision.NerdVision import NerdVision

    agent_settings['name'] = name
    agent_settings['api_key'] = api_key
    agent_settings['tags'] = tags

    from nerdvision import settings
    settings.configure_agent(agent_settings)

    api_key = settings.get_setting("api_key")
    if api_key is None:
        configure_logger().error("Stream hippo api key is not defined.")
        exit(314)

    hippo = NerdVision()
    hippo.start()
    return hippo


def configure_logger():
    from nerdvision import settings
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
