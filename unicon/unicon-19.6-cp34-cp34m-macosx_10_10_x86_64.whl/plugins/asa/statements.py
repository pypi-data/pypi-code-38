import time
from unicon.eal.dialogs import Statement
from unicon.eal.helpers import sendline

from .patterns import ASAPatterns
from .settings import ASASettings

from unicon.plugins.generic.statements import (
    connection_failure_handler,
    connection_refused_handler,
    bad_password_handler,
)

patterns = ASAPatterns()
settings = ASASettings()

def enable_password_handler(spawn, context, session):
    spawn.sendline(context['enable_password'])


def line_password_handler(spawn, context, session):
    spawn.sendline(context['line_password'])

def escape_char_handler(spawn):
    """ handles telnet login messages
    """
    # Wait a small amount of time for any chatter to cease from the
    # device before attempting to call sendline.

    prev_buf_len = len(spawn.buffer)
    for retry_number in range(
            settings.ESCAPE_CHAR_CALLBACK_PAUSE_CHECK_RETRIES):
        time.sleep(settings.ESCAPE_CHAR_CALLBACK_PAUSE_SEC)
        spawn.read_update_buffer()
        cur_buf_len = len(spawn.buffer)
        if prev_buf_len == cur_buf_len:
            break
        else:
            prev_buf_len = cur_buf_len

    spawn.sendline()

login_password = Statement(pattern=patterns.line_password,
                           action=line_password_handler,
                           args=None,
                           loop_continue=True,
                           continue_timer=False)

enable_password = Statement(pattern=patterns.enable_password,
                            action=enable_password_handler,
                            args=None,
                            loop_continue=True,
                            continue_timer=False)

escape_char_stmt = Statement(pattern=patterns.escape_char,
                             action=escape_char_handler,
                             args=None,
                             loop_continue=True,
                             continue_timer=False)

press_return_stmt = Statement(pattern=patterns.press_return,
                              action=sendline, 
                              args=None,
                              loop_continue=True,
                              continue_timer=False)

connection_refused_stmt = Statement(pattern=patterns.connection_refused,
                                    action=connection_refused_handler,
                                    args=None,
                                    loop_continue=False,
                                    continue_timer=False)

bad_password_stmt = Statement(pattern=patterns.bad_passwords,
                              action=bad_password_handler,
                              args=None,
                              loop_continue=False,
                              continue_timer=False)

disconnect_error_stmt = Statement(pattern=patterns.disconnect_message,
                                  action=connection_failure_handler,
                                  args={
                                  'err': 'received disconnect from router'},
                                  loop_continue=False,
                                  continue_timer=False)