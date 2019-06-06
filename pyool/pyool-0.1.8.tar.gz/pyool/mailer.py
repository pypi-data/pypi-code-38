import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 
from email import encoders
from .logger_setting import logger 
from datetime import datetime 
import os 
import time 


class Mailer: 

    def send(self, email_title, message, mail_server, mail_to_list, mail_cc_list
            , attached_file_path_list = None, attached_image_path_list = None, message_encode = "plain"
            , retry_time = 0, buffering = 5): 

        logger.info("Start setting up Mailer...")

        server = smtplib.SMTP_SSL(
        host = mail_server['host'], 
        port = mail_server['port']
        ) 
        
        msg = MIMEMultipart()

        # Setup the parameters of the message
        msg_to = mail_to_list
        msg_cc = mail_cc_list 

        msg['From'] = mail_server['from']
        msg['To'] = ', '.join(msg_to)
        msg['CC'] = ', '.join(msg_cc)
        msg['Subject'] = email_title

        logger.info("Compiling message...")
        msg.attach(MIMEText(message, message_encode))

        if attached_file_path_list != None: 
            for file_path in attached_file_path_list:
                if not os.path.isfile(file_path):
                    continue 
                
                with open(file_path, "rb") as fp: 
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(fp.read()) 

                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename = os.path.basename(file_path)) 
                msg.attach(part)


        if attached_image_path_list != None: 
            for image_path in attached_image_path_list:
                if not os.path.isfile(image_path):
                    continue 
                
                with open(image_path, "rb") as fp:
                    part = MIMEImage(fp.read()) 
                part.add_header('Content-Disposition', 'attachment', filename = os.path.basename(image_path)) 
                msg.attach(part)
        

        if mail_server['user']:
            # server.starttls()
            server.login(
                mail_server['user'],
                mail_server['pwd']
            )
        
        
        attempt = 0
        while attempt == 0 or attempt < retry_time:
            try: 
                server.sendmail(msg['From'], msg_to, msg.as_string())
                logger.info("Finish sending email.") 
                server.quit()
                return True 

            except Exception as e: 
                attempt += 1
                issue = e 
                message = "Attempt {}. {}. Retrying .....".format(attempt, issue)
                logger.error(message)
                time.sleep(buffering) 
                continue
                
        server.quit()
        raise RuntimeError("Cannot send email due to: {}".format(issue))

        
        
