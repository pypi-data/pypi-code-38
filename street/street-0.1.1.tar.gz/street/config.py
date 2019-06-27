from configparser import ConfigParser
import os


HOME = os.path.expanduser('~')
CONFIG_FILE = os.path.join(HOME, '.street.ini')
SECTION = 'browser'


def set_config(user_agent, cookie):
    config_parser = ConfigParser()
    config_parser.add_section(SECTION)
    config_parser.set(SECTION, 'user_agent', user_agent)
    config_parser.set(SECTION, 'cookie', cookie)

    with open(CONFIG_FILE, 'w') as config_file:
        config_parser.write(config_file)


def get_config():
    config_parser = ConfigParser()
    config_parser.read(CONFIG_FILE)
    user_agent = config_parser.get(SECTION, 'user_agent')
    cookie = config_parser.get(SECTION, 'cookie')

    return user_agent, cookie
