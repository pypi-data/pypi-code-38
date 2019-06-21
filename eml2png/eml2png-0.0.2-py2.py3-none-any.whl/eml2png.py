# -*- coding: utf-8 -*-
import email
import logging
import os

import imgkit

WKHTMLTOIMAGE = os.getenv('WKHTMLTOIMAGE', '/usr/bin/wkhtmltoimage')

logger = logging.getLogger(__name__)


def get_html_str_from_file(file_path, eml_str=None):
    """Get HTML part from EML file.

    Arguments:
        file_path ([str]): Input EML file

    Keyword Arguments:
        eml_str ([str]): EML string (default: None)

    Returns:
        [str]: EML HTML string
    """
    html_str = ''
    body_html = []
    body_text = []
    body = []
    email_msg = None
    if file_path and os.path.isfile(file_path):
        eml_str = open(file_path, 'r').read()
    if eml_str:
        email_msg = email.message_from_string(eml_str)
    if email_msg:
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
    return html_str if 'html' in html_str else '<pre>{}</pre>'.format(html_str)


def to_png(file_path, html_str=None, config=None, options=None):
    """Paint the EML to a single PNG image.

    Arguments:
        file_path ([str]): EML file path

    Keyword Arguments:
        html_str ([str]): EML HTML string (default: None)
        config: imgkit config (default: None)
        options: imgkit options (default: None)

    Returns:
        [bytes]: a PNG byte string.
    """
    if file_path and html_str is None:
        html_str = get_html_str_from_file(file_path)
    html_str = html_str if html_str else ''
    config = config if config else imgkit.config(wkhtmltoimage=WKHTMLTOIMAGE)
    options = options if options else {
        'format': 'png',
        'quiet': '',
    }
    return imgkit.from_string(html_str, False, config=config, options=options)
