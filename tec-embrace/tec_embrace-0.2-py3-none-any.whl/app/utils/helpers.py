from xml.etree.ElementTree import fromstring

class Utils:

    @staticmethod
    def remove_html_tags(text):
        """
        Remove HTML tags from text
        :param text: HTML text
        :return: Cleaned text
        """
        return ''.join(fromstring(text).itertext())
