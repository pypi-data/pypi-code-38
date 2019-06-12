# -*- coding: utf-8 -*-
# Description: Functions for sending mail with the running Outlook instance
# Author:  Hywel Thomas

u"""
Currently only works for windows!

Examples

send_with_outlook(to_list=u'forename.durname@blah.com',
                  subject=u'test subject',
                  body=u'test body')

send_html_with_outlook(to_list=u'forename.durname@blah.com',
                       subject=u'test subject',
                       html_body=u'<pre>test body</pre>')
"""

try:
    import win32com.client as win32
except:
    win32 = None


def send_with_outlook(to_list,
                      subject,
                      body):
    outlook = win32.Dispatch(u'outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = to_list
    mail.Subject = subject
    mail.body = body
    mail.send


def send_html_with_outlook(to_list,
                           subject,
                           html_body):
    outlook = win32.Dispatch(u'outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = to_list
    mail.Subject = subject
    mail.HTMLbody = html_body
    mail.send
