import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
from lxml import html
import json
import csv


def message_send():
    url = 'http://45.55.213.78/login'

    h = {'Accept': 'application/json, text/plain, */*',
         'Content-Type': 'application/json',
         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36', }
    useremail = input("enter chameleon username: ")
    password = input("enter chameleon account password: ")
    d = {"useremail": useremail, "userpassword": password}
    req = requests.session()
    response = req.post
    response = req.post(url, data=json.dumps(d), headers=h)

    final_page = req.get('http://45.55.213.78/getwebsitedata')
    data = final_page.text
    data.strip('/n')
    data = ''.join(data.split())
    data = json.loads(data)
    data = data.get('data')
    error_sites = []
    site = []

    for i in data:
        name = i['site_url']
        for j in i['sub_url_details']:
            for k in j['xpaths']:
                if k['status'] == False:
                    site.append(
                        {'name': name, 'xpath': k['xpath'], 'category': k['name']})

    keys = site[0].keys()
    with open("document.csv", "w") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(site)

    if site:
        fromaddr = input("enter the gmail username of sender: ")

        password = input("enter the password: ")
        toaddr = input("enter the receiver username: ")

        msg = MIMEMultipart()

        msg['From'] = fromaddr

        msg['To'] = toaddr

        msg['Subject'] = "error xpaths"

        body = "details of xpaths which have error is attached below"

        msg.attach(MIMEText(body, 'plain'))

        filename = "document.csv"
        attachment = open("document.csv", "rb")

        p = MIMEBase('application', 'octet-stream')

        p.set_payload((attachment).read())

        encoders.encode_base64(p)

        p.add_header('Content-Disposition',
                     "attachment; filename= %s" % filename)

        msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com', 587)

        s.starttls()

        s.login(fromaddr, password)

        text = msg.as_string()

        s.sendmail(fromaddr, toaddr, text)

        s.quit()


message_send()
