import time
import os

from .errornotification import ErrorNotification

from .filenamebuilder import build_file_name

from .readdebitsexcel import read_debits_excel

from .parsers import (
    parse_debits_headers, parse_debits_lines,
    calculate_last_line
)

from .validators import (
    validate_headers, validate_lines,
    validate_file
)

from .notifyerrors import notify_errors

from .writers import (
    stream_lines, stream_last_line
)


def generate_debits(cwd):
    for notification in execute_generation(cwd):
        if notification.has_errors():
            handle_errors(cwd, notification)
            return


def handle_errors(cwd, notification):
    errors_filename = os.path.join(cwd,'outputs/debit_errors_' + time.strftime("%Y%m%d-%H%M%S") + '.txt')
    with open(errors_filename, 'w') as stream:
        notify_errors(notification, stream)


def execute_generation(cwd):
    notification = ErrorNotification()

    excel_path = os.path.join(cwd, "inputs", "generar_debitos.xlsx")

    notification.collect_notifications(validate_file(excel_path))

    yield notification

    raw_data = read_debits_excel(excel_path)

    # procesar cabeceras de excel
    for page_data in raw_data:

        header_data = parse_debits_headers(page_data)
        notification.collect_notifications(validate_headers(header_data))
        yield notification

        debits_data = parse_debits_lines(page_data)
        notification.collect_notifications(validate_lines(debits_data))
        yield notification

        last_line = calculate_last_line(header_data, debits_data)

        filename = build_file_name(cwd, header_data)

        with open(filename, 'w') as file_stream:
            stream_lines(header_data, debits_data, file_stream)
            stream_last_line(last_line, file_stream)
