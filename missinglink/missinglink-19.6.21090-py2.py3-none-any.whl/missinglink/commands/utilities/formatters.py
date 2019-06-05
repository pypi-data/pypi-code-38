# -*- coding: utf-8 -*-
import dateutil.parser

DISPLAY_DATETIME_FORMAT = '%b %d, %H:%M'


def format_datetime(server_datetime):
    d = dateutil.parser.parse(server_datetime)
    return d.isoformat()


SHORT_TEXT_MAX_LENGTH = 20
LONG_TEXT_MAX_LENGTH = 50


def create_text_truncator(max_length):
    def truncate_text(text):
        if max_length <= 0:
            return text

        text = ' '.join(text.splitlines())

        if len(text) > max_length:
            text = text[:max_length] + '...'

        return text

    return truncate_text


truncate_short_text = create_text_truncator(SHORT_TEXT_MAX_LENGTH)
truncate_long_text = create_text_truncator(LONG_TEXT_MAX_LENGTH)
