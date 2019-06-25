"""
Module:
    unicon.plugins.generic

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
  This module defines the Generic settings to setup
  the unicon environment required for generic based
  unicon connection
"""
from unicon.settings import Settings
from unicon.plugins.generic.patterns import GenericPatterns

genpat = GenericPatterns()
class GenericSettings(Settings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'term length 0',
            'term width 0',
            'show version'
        ]
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console',
            'line console 0',
            'exec-timeout 0'
        ]
        self.HA_STANDBY_UNLOCK_COMMANDS = [
            'redundancy',
            'main-cpu',
            'standby console enable'
        ]
        self.BASH_INIT_COMMANDS = [
            'stty cols 200',
            'stty rows 200'
        ]

        self.SWITCHOVER_COUNTER = 50
        self.SWITCHOVER_TIMEOUT = 500
        self.HA_RELOAD_TIMEOUT = 500
        self.RELOAD_TIMEOUT = 300
        self.RELOAD_WAIT = 240
        self.CONSOLE_TIMEOUT = 60

        # When connecting to a device via telnet, how long (in seconds)
        # to pause before checking the spawn buffer
        self.ESCAPE_CHAR_CHATTY_TERM_WAIT = 0.25

        # number of cycles to wait for if the terminal is still chatty
        self.ESCAPE_CHAR_CHATTY_TERM_WAIT_RETRIES = 12

        # prompt wait delay
        self.ESCAPE_CHAR_PROMPT_WAIT = 0.25

        # prompt wait retries
        # (wait time: 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75 == total wait: 7.0s)
        self.ESCAPE_CHAR_PROMPT_WAIT_RETRIES = 7

        # Sometimes a copy operation can fail due to network issues,
        # so copy at most this many times.
        self.MAX_COPY_ATTEMPTS = 2

        # If configuration mode cannot be entered on a newly reloaded device
        # because HA sync is in progress, wait this many times and for this long
        self.CONFIG_POST_RELOAD_MAX_RETRIES = 20
        self.CONFIG_POST_RELOAD_RETRY_DELAY_SEC = 9

        # Default error pattern
        self.ERROR_PATTERN=[]

        # Number of times to retry for config mode by configure service.
        self.CONFIG_LOCK_RETRIES = 0
        self.CONFIG_LOCK_RETRY_SLEEP = 2

        # User defined login and password prompt pattern.
        self.LOGIN_PROMPT = None
        self.PASSWORD_PROMPT = None

        # Maximum number of retries for password handler
        self.PASSWORD_ATTEMPTS = 3

        # Ignore log messages before executing command
        self.IGNORE_CHATTY_TERM_OUTPUT = False

        # How long to wait for config sync after an HA reload.
        self.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 100

        self.DEFAULT_HOSTNAME_PATTERN = genpat.default_hostname_pattern

        # Traceroute error Patterns
        self.TRACEROUTE_ERROR_PATTERN = [\
                              '^.*(% )?DSCP.*does not match any topology',
                              'Bad IP (A|a)ddress', 'Ping transmit failed',
                              'Invalid vrf', 'Unable to find',
                              'No Route to Host.*',
                              'Destination Host Unreachable',
                              'Unable to initialize Windows Socket Interface',
                              'IP routing table .* does not exist',
                              'Invalid input',
                              'Unknown protocol -',
                              'bad context', 'Failed to resolve',
                              '(U|u)nknown (H|h)ost']

#TODO
#take addtional dialogs for all service
#move all commands to settings
#
