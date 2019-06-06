from html.parser import HTMLParser
from pyno import HTML as H, TreeNode


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parent_stack = [H.doc()]

    def handle_starttag(self, tag, attrs):
        self.parent_stack.append(TreeNode(tag,**dict(attrs)))
        if tag == 'img':
            self.handle_endtag(tag)


    def handle_endtag(self, tag):
        self.parent_stack[-2].args.append(self.parent_stack.pop())



    def handle_data(self, data):
        self.parent_stack[-1].args.append(data)


def pyno_parser(text):

    parser = MyHTMLParser()
    parser.feed(text)
    return parser.parent_stack[0]


