from browser import document, window

document.bind('click', ".RDNT-ignore_link", lambda evt: evt.preventDefault())


#----------------------------------------------------------------------
def open_link_(href):
    """"""
    def inset(evt):
        window.open(href, '_blank')
    return inset


for a in document.select('.RDNT-open_link'):
    a.bind('click', open_link_(a.attrs['href']))
    
