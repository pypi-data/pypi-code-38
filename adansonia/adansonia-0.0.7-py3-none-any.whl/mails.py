#!/usr/bin/env python
# coding: utf-8

import pickle
import os.path
import base64
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


class DaHoldingSender():
    def __init__(self, tokenfile, credfile):
        scopes = ['https://www.googleapis.com/auth/gmail.compose']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(tokenfile):
            with open(tokenfile, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credfile, scopes)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(tokenfile, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def send_email(self, to, subject, text, attachment=None):
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = 'daholding@baobab.bz'
        message['subject'] = subject
        body = MIMEText(text)  # convert the body to a MIME compatible string
        message.attach(body)

        if attachment is not None:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(attachment, "rb").read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition', 'attachment', filename=attachment)
            message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        self.service.users().messages().send(
            userId='me', body={
                'raw': raw
            }).execute()
