from apistar.client.encoders import BaseEncoder


class XMLEncoder(BaseEncoder):
    media_type = 'application/xml'

    def encode(self, options, content):
        options['headers']['Content-Type'] = 'application/xml'

        # If the content is not a stream-like object nor a bytestring,
        # turn it into a bytestring
        if not isinstance(content, bytes) and not hasattr(content, 'read'):
            if not isinstance(content, str):
                content = str(content)
            content = content.encode('utf-8')

        options['data'] = content
