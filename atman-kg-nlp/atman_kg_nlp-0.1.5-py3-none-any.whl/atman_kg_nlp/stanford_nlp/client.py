from stanfordnlp.server.client import *
import requests


class LanguageCoreNLPClient(CoreNLPClient):
    '''
    This class inherits from CoreNLPClient to support language dependant
    parsing.
    '''

    def _request(self, buf, properties, language='en'):
        """Send a request to the CoreNLP server.

        :param (str | unicode) text: raw text for the CoreNLPServer to parse
        :param (dict) properties: properties that the server expects
        :return: request result
        """
        self.ensure_alive()

        try:
            input_format = properties.get("inputFormat", "text")
            if input_format == "text":
                ctype = "text/plain; charset=utf-8"
            elif input_format == "serialized":
                ctype = "application/x-protobuf"
            else:
                raise ValueError("Unrecognized inputFormat " + input_format)

            r = requests.post(self.endpoint,
                              params={'properties': str(properties),
                                      'pipelineLanguage': language},
                              data=buf, headers={'content-type': ctype},
                              timeout=(self.timeout * 2) / 1000)
            r.raise_for_status()
            return r
        except requests.HTTPError as e:
            if r.text == "CoreNLP request timed out. " \
                         "Your document may be too long.":
                raise TimeoutException(r.text)
            else:
                raise AnnotationException(r.text)

    def annotate(self, text, annotators=None, properties=None, language='en'):
        """Send a request to the CoreNLP server.

        :param (str | unicode) text: raw text for the CoreNLPServer to parse
        :param (list | string) annotators: list of annotators to use
        :param (dict) properties: properties that the server expects
        :return: request result
        """
        # set properties for server call
        if properties is None:
            properties = self.default_properties
            properties.update({
                'annotators': ','.join(annotators or self.default_annotators),
                'inputFormat': 'text',
                'outputFormat': 'json'
            })
        elif "annotators" not in properties:
            properties.update({'annotators': ','.join(
                annotators or self.default_annotators)})

        if language == 'zh':
            text = text.replace('(', '（') \
                    .replace(')', '）') \
                    .replace(',', '，')

        # make the request
        r = self._request(text.encode('utf-8'), properties, language)
        return r.json()
