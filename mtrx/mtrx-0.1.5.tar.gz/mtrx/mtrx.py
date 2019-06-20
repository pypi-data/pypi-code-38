import itertools, io, pyqrcode, os, sys, time, smtplib, requests, dns.resolver, autopy
# from __future__ import absolute_import, division, print_function, unicode_literals

def qrcode(text, Format):
    """mtrx.qrcode(text='YourText', Format='ImageFormat')
    Create Your QRcode just with 1 line and 2 variable
    formats = 'svg', 'eps', 'terminal'
    """
    #the QR code
    if Format == 'svg':
    	pyqrcode.create('%s'%text).svg('%s.%s'%(text, Format), scale=8)
    elif Format == 'eps':
	    pyqrcode.create('%s'%text).eps('%s.%s'%(text, Format), scale=2)
    elif Format == 'terminal':
        print(pyqrcode.create('%s'%text).terminal(quiet_zone=1))
    else:
        print('args not valid')

def timeNow():
    """Get now time"""
    return '%s:%s:%s'%(time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)

def dateNow():
    """Get now data"""
    return '%s/%s/%s'%(time.localtime().tm_mday ,time.localtime().tm_mon ,time.localtime().tm_year)

def sendgmail(username, password, to, text):
    """mtrx.sendgmail(username='yourgmail', password='yourpassword', to='togmail', text='yourtext')
    send gmail with 1 line and 4 variable"""
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login('%s'%username, '%s'%password)
    server.sendmail('%s'%username, '%s'%to, '%s'%text)
    server.close()

def myip():
    """Get Your IP"""
    resp = requests.get('https://httpbin.org/ip').json()['origin']
    return resp[:resp.find(',')]

def DNS(url):
    """mtrx.DNS(url='SiteURL')
    found website DNS(domain name server)"""
    for server in dns.resolver.query('%s'%url,'NS'):
        return server.target

def screensh():
    """mtrx.screensh()
    get screenshot to easy"""
    a = '%s-%s-%s-%s-%s-%s'%(time.localtime().tm_year,time.localtime().tm_mon, time.localtime().tm_mday, time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
    autopy.bitmap.capture_screen().save('%s.png'%a)

def download(url):
    """mtrx.download(url='downloadLink')
    download any file to easy"""
    name = url.rsplit('/', 1)[1]
    type = requests.head(url).headers.get('content-type')
    data = requests.get(url).content
    with open('%s.%s'%(name, type[type.find('/')+1:]), 'wb') as f:
        f.write(data)

def learnpy():
    print('t.me/learnpy\nLearn a new thing from python each day.')
