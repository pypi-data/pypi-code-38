import os
import mandrill
import codecs
import base64


class MailClient(object):

    @staticmethod
    def send_mail(api_token, email_to: list, email_from: str, name_from: str, subject: str, language='NL', content=None, attachment=None):
        """
        Send a mail with the salureconnect layout and using mandrill
        :param api_token: the mandrill API token
        :param email_to: a list with name and mailadress to who the mail must be send
        :param email_from: the mailaddress from the sender. Should be enabled in mandrill
        :param name_from: The name from the sender. Will be printed at the bottom of the mail
        :param subject: The subject of the email
        :param language: Determines the salutation and greeting text. For example Beste or Dear
        :param content: The message of the email
        :param attachment: The attachment of an email loaded as binary file (NOT the location of the file)
        :return: If the sending of the mail is successful or not
        """
        mandrill_client = mandrill.Mandrill(api_token)
        # Load the html template for e-mails
        html_file_location = '{}/templates/mail_salureconnect.html'.format(os.path.dirname(os.path.abspath(__file__)))
        html_file = codecs.open(html_file_location, 'r')
        html = html_file.read()
        if language == 'NL':
            salutation = 'Beste '
            greeting_text = 'Met vriendelijke groet,'
        else:
            salutation = 'Dear '
            greeting_text = 'Kind regards,'

        # Set attachment. Do not in loop because of errors
        if attachment is not None:
            opened_attachment = attachment.read()
            encoded_attachment = base64.b64encode(opened_attachment).decode('utf-8')

        # Pick the configurations from the config file and create the mail
        for i in email_to:
            new_html = html.replace('{', '{{'). \
                replace('}', '}}'). \
                replace('{{subject}}', '{subject}'). \
                replace('{{title}}', '{title}'). \
                replace('{{salutation}}', '{salutation}'). \
                replace('{{name}}', '{name}'). \
                replace('{{content}}', '{content}'). \
                replace('{{greeting}}', '{greeting}').format(subject=subject, title=subject, salutation=salutation, name=i['name'], content=content, greeting=greeting_text)
            if attachment is None:
                mail = {
                    'from_email': email_from,
                    'from_name': name_from,
                    'subject': subject,
                    'html': new_html,
                    'to': [{'email': i['mail'],
                            'name': i['name'],
                            'type': 'to'}]
                }
            else:
                mail = {
                    'from_email': email_from,
                    'from_name': name_from,
                    'attachments': [{'content': encoded_attachment,
                                     'name': attachment.name.split('/')[-1]
                                     }],
                    'subject': subject,
                    'html': new_html,
                    'to': [{'email': i['mail'],
                            'name': i['name'],
                            'type': 'to'}]
                }
            # Send the mail
            mandrill_client.messages.send(mail, False, 'Main Pool')

