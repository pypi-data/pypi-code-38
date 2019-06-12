from nerdvision.Utils import Utils

__version__ = '0.0.8'
# this has to be set here for the test coverage to work
__name__ = 'nerdvision'
agent_name = 'NerdVision Python Agent'

__version_major__ = '0'
__version_minor__ = '0'
__version_micro__ = '8'

__props__ = {
    '__Git_Branch__': '0.0.8',
    '__Git_Commit_Id__': '8569199da60559caf22f8db526d0ab36299c322a',
    '__Git_Commit_Time__': '2019-06-12 18:12:08+02:00',
    '__Git_Dirty__': 'False',
    '__Git_Remote_Origin_Url__': 'https://gitlab-ci-token:iktdymc852pDyUeXbw5A@gitlab.com/intergral/agents/python-client.git',
    '__Git_Tags__': '[<git.TagReference "refs/tags/0.0.1">, <git.TagReference "refs/tags/0.0.2">, <git.TagReference "refs/tags/0.0.3">, <git.TagReference "refs/tags/0.0.4">, <git.TagReference "refs/tags/0.0.5">, <git.TagReference "refs/tags/0.0.6">, <git.TagReference "refs/tags/0.0.7">, <git.TagReference "refs/tags/0.0.8">]',

    '__X_CI_Pipeline_Id__': '',
    '__X_CI_Pipeline_Iid__': '',
    '__X_CI_Pipeline_Source__': '',
    '__X_CI_Pipeline_Url__': '',
    '__X_CI_Project_Name__': '',
}


def start(api_key, name=None, tags=None, agent_settings=None):
    from nerdvision.NerdVision import NerdVision

    if agent_settings is None:
        agent_settings = {}

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

    our_logger = logging.getLogger("nerdvision")
    # logging has been configured dont do it again
    # noinspection PyUnresolvedReferences
    if Utils.is_python_3() and our_logger.hasHandlers():
        return our_logger
    elif not Utils.is_python_3() and len(our_logger.handlers) != 0:
        return our_logger

    formatter = logging.Formatter('%(asctime)s NerdVision: [%(levelname)s] %(message)s', datefmt='%b %d %H:%M:%S')

    if log_file is not None:
        file_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10000000, backupCount=5, encoding=None,
                                                            delay=0)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        our_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()

    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    our_logger.propagate = False
    our_logger.setLevel(level)

    our_logger.addHandler(stream_handler)

    return our_logger
