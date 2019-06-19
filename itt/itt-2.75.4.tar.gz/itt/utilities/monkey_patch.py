
import logging_helper

logging = logging_helper.setup_logging()


def monkey_patch():

    """ Monkey patch requests' default_user_agent to add user and tool identification """

    try:
        TOOL_NAME

    except NameError:
        import requests
        import getpass
        import sys

        try:
            TOOL_NAME = sys.argv[0].split(u'\\')[-1].split(u'/')[-1].split(u'.')[0]

        except:
            TOOL_NAME = u'itt_general'

        try:
            USERNAME = getpass.getuser()

        except:
            USERNAME = u'Unknown user'

        try:
            requests.utils.MONKEY_PATCHED_DEFAULT_USER_AGENT

        except AttributeError:
            default_user_agent = requests.utils.default_user_agent()
            requests.utils.MONKEY_PATCHED_DEFAULT_USER_AGENT = ("{user}; {tool}; {default_user_agent}"
                                                                .format(user=USERNAME,
                                                                        tool=TOOL_NAME,
                                                                        default_user_agent=default_user_agent))

            def monkey_patched_default_user_agent():
                logging.debug(u'User-Agent:{user_agent}'
                              .format(user_agent=requests.utils.MONKEY_PATCHED_DEFAULT_USER_AGENT))

                return requests.utils.MONKEY_PATCHED_DEFAULT_USER_AGENT

            requests.utils.default_user_agent = monkey_patched_default_user_agent
