import email.mime.multipart
import email.mime.text
import email.utils
import smtplib
import copy
import datetime

import markdown
import yaml
import click

from .isholiday import isholiday
from .digest import generate_digest
from .version import TAGLINE

htmltemplate = """
<!DOCTYPE html>
<html>
<head>
        <meta charset="utf-8">
        <title>Polední menu</title>
        <style>
            ul {{
                list-style-type: disc;
            }}
        </style>
</head>
<body>
{body}
</body>
</html>
"""


def htmlize(text):
    """Return HTML version of markdown text"""
    htmlized = markdown.markdown(
        text,
        output_format="xhtml5", safe_mode="escape",
    )
    htmlversion = htmltemplate.format(body=htmlized)
    return htmlversion


def send_html_email(
    textpart, htmlpart, subject, recipients,
    server="localhost",
    sender="Foodmaster <foodmaster@localhost>",
):
    """
    Sends multipart alternative e-mail
    """

    msgtpl = email.mime.multipart.MIMEMultipart('alternative')
    msgtpl['Subject'] = subject
    msgtpl['From'] = email.utils.formataddr(email.utils.parseaddr(sender))
    msgtpl['Date'] = email.utils.formatdate(localtime=True)
    msgtpl.attach(email.mime.text.MIMEText(textpart))
    msgtpl.attach(email.mime.text.MIMEText(htmlpart, 'html'))

    with smtplib.SMTP(server) as smtp:
        for r in recipients:
            msg = copy.deepcopy(msgtpl)
            msg['Message-id'] = email.utils.make_msgid('poledni-menu')
            msg['To'] = email.utils.formataddr(email.utils.parseaddr(r))
            smtp.send_message(msg)


def send_email_digest(config):
    dow = (
        "pondělí", "úterý", "středu",
        "čtvrtek", "pátek", "sobotu", "neděli",
    )
    mname = (
        "ledna", "února", "března", "dubna", "května", "června", "července",
        "srpna", "září", "října", "listopadu", "prosince",
    )

    td = datetime.date.today()
    if isholiday(td):
        return
    subject = (
        "\N{Fork and Knife With Plate} Polední nabídka pro"
        " {dow} {day}. {mname}"
    ).format(
        dow=dow[td.weekday()],
        day=td.day,
        mname=mname[td.month-1],
    )
    menu = config.get("menu", [])
    textmenu = "\n".join([
        *generate_digest(menu),
        TAGLINE,
    ])
    htmlmenu = htmlize(textmenu)
    emailargs = config.get("email", {})
    send_html_email(textmenu, htmlmenu, subject, **emailargs)


@click.command()
@click.argument("config", type=click.File())
def email_digest(config):
    """
    E-mail daily menu digest for a list of places.
    """
    send_email_digest(yaml.safe_load(config))
