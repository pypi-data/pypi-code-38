# -*- coding: utf-8 -*-
import email
import logging
import os

import imgkit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WKHTMLTOIMAGE = os.getenv('WKHTMLTOIMAGE', '/usr/bin/wkhtmltoimage')

logger = logging.getLogger(__name__)


def get_html_str_from_file(file_path):
    """Get HTML part from EML file.

    Arguments:
        file_path ([str]): Input EML file

    Returns:
        [str]: EML HTML string
    """
    html_str = ''
    body_html = []
    body_text = []
    body = []
    if file_path and os.path.isfile(file_path):
        email_str = open(file_path, 'r').read()
        email_msg = email.message_from_string(email_str)
        # If message is multi part we only want the text version of the body,
        # this walks the message and gets the body.
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == 'text/html':
                    body_html.append(part.get_payload(decode=True))
                elif part.get_content_type() == 'text/plain':
                    body_text.append(part.get_payload(decode=True))
            body = body_html if len(body_html) > 0 else body_text
        else:
            body.append(email_msg.get_payload(decode=True))
        html_str = '<br>'.join([b.decode('utf8') for b in body])
    return '<pre>{}</pre>'.format(html_str) if 'html' not in html_str else html_str


def to_png(file_path, html_str=None):
    """Paint the EML to a single PNG image.

    Arguments:
        file_path ([str]): description

    Keyword Arguments:
        html_str ([str]): description (default: None)

    Returns:
        [bytes]: a PNG byte string.
    """
    if file_path and html_str is None:
        html_str = get_html_str_from_file(file_path)
    html_str = html_str if html_str else ''
    config = imgkit.config(wkhtmltoimage=WKHTMLTOIMAGE)
    options = {
        'format': 'png',
        'quiet': '',
    }
    return imgkit.from_string(html_str, False, config=config, options=options)
