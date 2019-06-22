
import aiohttp
import asyncio
import base64
import logging
import re

from colibris.email.base import EmailBackend


VERSION = '1.0.0'
REQUEST_TIMEOUT = 60

logger = logging.getLogger(__name__)


class SendGridBackend(EmailBackend):
    BASE_URL = 'https://api.sendgrid.com/v3'
    SEND_MAIL_ENDPOINT = '/mail/send'

    def __init__(self, api_key, **kwargs):
        self.api_key = api_key

        super().__init__(**kwargs)

    def send_messages(self, email_messages):
        asyncio.ensure_future(self.send_messages_async(email_messages))

    async def send_messages_async(self, email_messages):
        for i, message in enumerate(email_messages):
            logger.debug('sending message %d/%d', i + 1, len(email_messages))

            try:
                await self.send_message(message)

            except Exception as e:
                logger.error('failed to send message (%s): %s', message, e, exc_info=True)

    async def send_message(self, message):
        personalization = {}

        if message.subject:
            personalization['subject'] = message.subject

        if message.to:
            personalization['to'] = [{'email': e} for e in message.to]

        if message.cc:
            personalization['cc'] = [{'email': e} for e in message.cc]

        if message.bcc:
            personalization['bcc'] = [{'email': e} for e in message.bcc]

        content_items = [{
            'type': 'text/plain',
            'value': message.body
        }]

        if message.html:
            content_items.append({
                'type': 'text/html',
                'value': message.html
            })

        attachments = []
        for content, mimetype, filename in message.attachments:
            attachments.append({
                'content': base64.b64encode(content).decode(),
                'type': mimetype,
                'filename': filename
            })

        body = {
            'personalizations': [
                personalization
            ],
            'from': {
                'email': message.from_
            },
            'content': content_items
        }

        if attachments:
            body['attachments'] = attachments

        if message.reply_to:
            body['reply_to'] = {'email': message.reply_to}

        await self.api_request('POST', self.SEND_MAIL_ENDPOINT, body=body)

    async def api_request(self, method, endpoint, headers=None, body=None):
        url = self.BASE_URL + endpoint
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        headers = headers or {}
        headers.update(self.make_auth_header())

        logger.debug('requesting %s %s', method, url)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=body, headers=headers) as response:
                    if response.status >= 400:
                        logger.warning('got status {}'.format(response.status))
                        response_body = await response.read()
                        logger.error('response body was: \n    %s', re.sub('\n', '\n    k', response_body.decode()))

                    else:
                        logger.debug('API request succeeded')

        except asyncio.TimeoutError:
            logger.error('timeout waiting for response')

    def make_auth_header(self):
        return {'Authorization': 'Bearer {}'.format(self.api_key)}
