# coding=utf8
"""SMTP

Wrapper for python smtp module
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-17"

# Python imports
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
from os.path import basename

# Init the local variables
__mdSMTP = {
	"host": "localhost",
	"port": 25,
	"tls": False,
	"passwd": ""
}

# Init the last error message
__msError = '';

# Create the defines
OK = 0
ERROR_UNKNOWN = -1
ERROR_CONNECT = -2
ERROR_LOGIN = -3
ERROR_BODY = -4

def init(host="localhost", port=25, tls=False, user=None, passwd=None):
	"""init

	Called to change/set any SMTP information before sending out any e-mails

	Args:
		host {str} -- The hostname of the SMTP server
		port {uint} -- The port on the host
		tls {bool} -- Set to True if we need TLS
		user {str} -- The authorization username
		passwd {str} -- The authorization password

	Returns:
		None
	"""

	# Import the module var
	global __mdSMTP

	# If the host is set
	if host:
		__mdSMTP['host'] = host

	# If the port is set
	if port:
		__mdSMTP['port'] = port

	# If we need TLS
	if tls:
		__mdSMTP['tls'] = tls

	# If the user is set
	if user:
		__mdSMTP['user'] = user

	# If the passwd is set
	if passwd:
		__mdSMTP['passwd'] = passwd

def lastError():
	"""Last Error

	Returns the last error message if there is one

	Returns:
		str
	"""
	global __msError
	return __msError

def send(to, subject, text_body = None, html_body = None, from_='root@localhost', bcc=None, attachments=None):
	"""Send

	Sends an e-mail to one or many addresses

	Arguments:
		to {str|str[]} -- One or email addresses to send to
		subject {str} -- The email's subject
		body {str} -- The main content of the email
		from_ {str} -- The from address of the email, optional
		bcc {str|str[]} -- Blind carbon copy addresses, optional
		attachments

	Returns:
		bool
	"""

	# Import the module vars
	global __msError, __mdSMTP

	# If the to is not a list
	if not isinstance(to, (list,tuple)):
		to = [to]

	# Create a new Mime MultiPart message
	oMMP = MIMEMultipart()
	oMMP['From'] = from_
	oMMP['To'] = ', '.join(to)
	oMMP['Date'] = formatdate()
	oMMP['Subject'] = subject

	# Check that text or html body is set
	if not text_body and not html_body:
		return ERROR_BODY

	# Attach the main message
	if text_body:
		oMMP.attach(MIMEText(text_body, 'plain'))

	if html_body:
		oMMP.attach(MIMEText(html_body, 'html'))

	# If there's any attachments
	if attachments:

		# Loop through the attachments
		for m in attachments:

			# If we got a string
			if isinstance(m, basestring):

				# Assume it's a file and open it
				with open(m, "rb") as rFile:
					oMMP.attach(MIMEApplication(
						rFile.read(),
						Content_Disposition='attachment; filename="%s"' % basename(m),
						Name=basename(m)
					))

			# Else if we get a dict
			elif isinstance(m, dict):

				# Add it
				oMMP.attach(MIMEApplication(
					m['body'],
					Content_Disposition='attachment; filename="%s"' % m['filename'],
					Name=m['filename']
				))

			# Unknown type
			else:
				raise ValueError(m)

	# Generate the body
	sBody = oMMP.as_string()

	# Catch any Connect or Authenticate Errors
	try:

		# Create a new instance of the SMTP class
		oSMTP = smtplib.SMTP(__mdSMTP['host'], __mdSMTP['port'])

		# If we need TLS
		if __mdSMTP['tls']:

			# Start TLS
			oSMTP.starttls()

		# If there's a username
		if __mdSMTP['user']:

			# Log in with the given credentials
			oSMTP.login(__mdSMTP['user'], __mdSMTP['passwd'])

		# Try to send the message, then close the SMTP
		oSMTP.sendmail(from_, to, sBody)
		oSMTP.close()

		# Return ok
		return OK

	# If there's a connection error
	except smtplib.SMTPConnectError as e:
		__msError = str(e.args)
		return ERROR_CONNECT

	# If there's am authentication error
	except smtplib.SMTPAuthenticationError as e:
		__msError = str(e.args)
		return ERROR_LOGIN

	# If there's any other error
	except smtplib.SMTPException as e:
		__msError = str(e.args)
		return ERROR_UNKNOWN
