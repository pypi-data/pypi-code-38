from __future__ import print_function

import logging

import boto3
from botocore.exceptions import ClientError

from halo_flask.logs import log_json
from .settingsx import settingsx

settings = settingsx()

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = "<contact@rtpricer.com>"

# Replace recipient@example.com with a "To" address. If your account
# is still in the sandbox, this address must be verified.
RECIPIENT = "rtpricer@gmail.com"

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the
# ConfigurationSetName=CONFIGURATION_SET argument below.
CONFIGURATION_SET = "ConfigSet"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = settings.AWS_REGION

# The subject line for the email.
SUBJECT = "contact form"

logger = logging.getLogger(__name__)

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
             )

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Amazon SES Test (SDK for Python)</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>
</body>
</html>
            """

# The character encoding for the email.
CHARSET = "UTF-8"


def send_mail(req_context, vars, from1=None, to=None):
    """

    :param req_context:
    :param vars:
    :param from1:
    :param to:
    :return:
    """
    name1 = vars["name1"]
    email1 = vars["email1"]
    message1 = vars["message1"]
    contact1 = vars["contact1"]
    body = '<p>name:'+name1+'</p>'+'<p>email:'+email1+'</p>'+'<p>message:'+message1+'</p>'+'<p>contact:'+contact1+'</p>'
    BODY_HTML = """<html><head></head><body>"""+body+"""</body></html> """
    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=settings.AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        logger.error("failed to send mail", extra=log_json(req_context, vars, e))
        return False
    else:
        logger.info("Email sent! Message ID:" + response['ResponseMetadata']['RequestId'], extra=log_json(req_context))
        return True