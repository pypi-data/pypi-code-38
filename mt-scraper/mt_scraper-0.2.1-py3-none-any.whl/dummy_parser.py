from html.parser import HTMLParser

class MyDummyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.a_tag = False
        self.h1_tag = False
        self.p_tag = False
        self.obj = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.h1_tag = True
        elif tag == 'p':
            self.p_tag = True
        elif tag == 'a':
            self.a_tag = True
            for (attr, value, ) in attrs:
                if attr == 'href':
                    self.obj['link'] = value

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.h1_tag = False
        elif tag == 'p':
            self.p_tag = False
        elif tag == 'a':
            self.a_tag = False

    def handle_data(self, data):
        if self.h1_tag:
            self.obj['header'] = data
        elif self.p_tag and not self.a_tag:
            self.obj['article'] = data
