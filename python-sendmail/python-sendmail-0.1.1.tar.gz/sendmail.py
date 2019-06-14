import os
from io import open
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import mimetypes
import click


def get_smtp_service(host="127.0.0.1", port=25, ssl=False, user=None, password=None):
    if ssl:
        smtp_service = smtplib.SMTP_SSL(host, port)
    else:
        smtp_service = smtplib.SMTP(host, port)
    if user and password:
        smtp_service.login(user, password)
    return smtp_service


def get_message(from_address, to_address, content, subject, attachs=None, is_html_content=False, content_encoding="utf-8"):
    message = MIMEMultipart()
    if subject:
        message["Subject"] = subject
    message["From"] = from_address
    message["To"] = to_address

    if is_html_content:
        main_content = MIMEText(content, "html", content_encoding)
    else:
        main_content = MIMEText(content, "plain", content_encoding)
    message.attach(main_content)

    attachs = attachs or []
    for attach in attachs:
        basename = None
        part = None
        with open(attach, "rb") as attach_file:
            basename = os.path.basename(attach)
            part = MIMEApplication(attach_file.read(), Name=basename)
        part.add_header('Content-Disposition', 'attachment', filename=basename)
        message.attach(part)

    return message


def sendmail(from_address, to_address, content, subject, attachs=None, is_html_content=False, content_encoding="utf-8", host="127.0.0.1", port=25, ssl=False, user=None, password=None):
    smtp_service = get_smtp_service(host, port, ssl, user, password)
    message = get_message(from_address, to_address, content, subject, attachs, is_html_content, content_encoding)
    smtp_service.send_message(message)
    smtp_service.quit()


@click.command()
@click.option("-f", "--from-address", required=True, help="Sender's mail address, e.g. Sender Name <sender@exmaple.com> or sender@example.com")
@click.option("-t", "--to-address", required=True, help="Recipient's mail address, e.g. Recipient Name <recipient@exmaple.com> or recipient@example.com")
@click.option("-s", "--subject", help="Mail subject")
@click.option("-a", "--attach", multiple=True, required=False, help="Attachment file path, can use multiple times.")
@click.option("--html", is_flag=True, help="The content is html format")
@click.option("-e", "--encoding", default="utf-8", help="Encoding of the content, defaults to utf-8")
@click.option("-h", "--host", default="127.0.0.1", help="Email server address")
@click.option("-p", "--port", default=25, help="Email server port")
@click.option("--ssl", is_flag=True, help="Email server use ssl")
@click.option("-u", "--user", help="Login user")
@click.option("-P", "--password", help="Login password")
@click.argument("content", nargs=1, required=False)
def main(from_address, to_address, subject, content, attach, html, encoding, host, port, ssl, user, password):
    """Send an email via command line.
    
    Note: 
    
    If CONTENT is not provided in command line, will read it from STDIN.
    """
    if not content:
        content = os.sys.stdin.read()
    sendmail(from_address, to_address, content, subject, attach, html, encoding, host, port, ssl, user, password)
    click.echo("mail with subject \"{subject}\" from {from_address} to {to_address} was sent.".format(
        subject=subject or "(no subject)",
        from_address=from_address,
        to_address=to_address
        ))


if __name__ == "__main__":
    main()
