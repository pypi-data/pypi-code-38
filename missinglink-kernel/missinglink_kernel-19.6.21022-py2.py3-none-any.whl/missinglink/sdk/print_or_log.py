import logging
import os


logger = logging.getLogger('missinglink')


def _actual_print_update(msg, *args):
    if args:
        msg = msg % args

    print(msg)


print_update_info = _actual_print_update if os.environ.get('ML_PRINT_UPDATE') == '1' else logger.info
print_update_warning = _actual_print_update if os.environ.get('ML_PRINT_UPDATE') == '1' else logger.warning
print_update_debug = _actual_print_update if os.environ.get('ML_PRINT_UPDATE') == '1' else logger.debug
print_update_error = _actual_print_update if os.environ.get('ML_PRINT_UPDATE') == '1' else logger.error
print_update_forced = _actual_print_update
