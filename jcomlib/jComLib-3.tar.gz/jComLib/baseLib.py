import smtplib
import datetime
import imaplib
import email
import time

def transmit(smtpServerUrl, emailAddress, emailPassword, receiverEmailAddress, namePrefix, messageToSend):
    server=smtplib.SMTP(smtpServerUrl, 587)
    server.starttls()
    server.login(emailAddress, emailPassword)
    MessagePrefixTime=(str(datetime.datetime.now().time())[:-10])
    MessagePrefixTimeMin=MessagePrefixTime[:2]
    MessagePrefixTimeSec=MessagePrefixTime[-2:]
    MessageOutput=namePrefix+"@"+MessagePrefixTimeMin+"."+MessagePrefixTimeSec+"-"+messageToSend
    server.sendmail(emailAddress, receiverEmailAddress, MessageOutput)
    server.quit()
    return 1
def receive(imapServerUrl, emailAddress, emailPassword, folderName):
    server=imaplib.IMAP4_SSL(imapServerUrl)
    server.login(emailAddress, emailPassword)
    server.select(folderName)
    (retcode, messages)=server.search(None, '(UNDELETED)')
    if retcode == 'OK':
        for num in messages[0].split() :
            typ, data = server.fetch(num,'(RFC822)')
            raw = email.message_from_bytes(data[0][1])
            time.sleep(1)
            server.store(num, '+FLAGS', '\\Deleted')
            return raw
    server.logout()
def bodyFromMessage(message):
    if message.is_multipart():
        return str(get_body(message.get_payload(0)))[2:-5]
    else:
        return str(message.get_payload(None,True))[2:-5]
