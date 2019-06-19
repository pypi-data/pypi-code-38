from lbCVMFSReporting.LbReport import LbCVMFSReport
from HTMLUtils import HTMLUtils
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import smtplib
from os.path import basename


class LbReportEmailer:

    def __init__(self, date, send_from, send_to, subject):
        report = LbCVMFSReport(date)
        jsonData = report.convertDataLogsToJson()
        converter = HTMLUtils(jsonData)
        htmlData = converter.getHtml()
        self._send_mail(send_from, send_to, subject, htmlData)

    def _send_mail(self, send_from, send_to, subject, text, files=None,
                   server="cernmx.cern.ch"):
        assert isinstance(send_to, list)

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text, 'html'))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % \
                                          basename(f)
            msg.attach(part)

        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
