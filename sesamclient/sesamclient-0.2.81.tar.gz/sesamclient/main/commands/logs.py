# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import shutil
import sys

from ..utils import print_item_list, exit_with_error


def get_logs_cmd(connection, args):
    # TODO: filtering
    logs = connection.get_logs()
    print_item_list(logs, args)


def get_log_content_cmd(connection, args):
    log_content = connection.get_log_content(args.log_id)
    if log_content is None:
        exit_with_error("No log with id '%s' was found!" % (args.log_id,))
    shutil.copyfileobj(log_content, sys.stdout.buffer)
    sys.stdout.flush()
