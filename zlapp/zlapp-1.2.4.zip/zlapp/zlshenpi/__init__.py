from html.parser import HTMLParser
from html.entities import name2codepoint

class myhtml(HTMLParser):
    def __init__(self):
        self.key=''
        self.value=''
        self.count=0
        self.d={}
        HTMLParser.__init__(self)

    def handle_starttag(self,tag,attrs):
        if tag=='tr':
            self.count=0

        if tag=='td' :
            self.count+=1

    def handle_data(self,data):

        if self.count==1:
            self.key=data.strip().replace('\n','').replace('\r','')


        if self.count==2:
            self.d[self.key]=data.strip().replace('\n','').replace('\r','')
            self.count=0

def ext_shenpi(page,quyu=None):
    parser=myhtml()
    parser.feed(page)

    result=parser.d
    return result 


