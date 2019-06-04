from mistune import Renderer
from urllib.parse import urlsplit

def url_is_absolute(url):
    return bool(urlsplit(url, scheme='https').netloc)


class LinkRenderer(Renderer):
    def __init__(self):
        self.urls = []
        super().__init__()

    def link(self, link, title, text):
        if url_is_absolute(link):
            self.urls.append(link)