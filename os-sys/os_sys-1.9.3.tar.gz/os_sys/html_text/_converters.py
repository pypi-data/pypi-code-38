import requests
from bs4 import BeautifulSoup
def obj_type(obj):
    m = type(obj)
    t = m
    m = str(t).replace('<class \'', '')
    t = m
    m = str(t).replace('\'>', '')
    return m
def text(url, print_text=False):
    from bs4 import BeautifulSoup

    import requests
    html = str(requests.get(url).content)
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    text = text.replace('\\n', '\n')
    text = str(text)
    if print_text:
        print(text)
    else:
        return text
from bs4 import BeautifulSoup
import requests

def get_links(url):
    html = requests.get(url).content
    bsObj = BeautifulSoup(html, 'lxml')

    links = bsObj.findAll('a')
    finalLinks = list()
    for link in links:
        finalLinks.append(link.attrs['href'])
    return finalLinks
def links(url, print_links=False):
    links = _get_links(url)
    if print_links:
        print(links)
    return links
def text2html(text, *alerts):
    if not str(obj_type(text)) == 'str':
        raise TypeError('expected a string by text but get a %s' % str(obj_type))
    alert = list(alerts)
    html_code = '<!DOCTYPE html>\n<html>'
    text = text.replace('\\n', '\n')
    if not alert == []:
        mystr = ''.join('<script>')
        for i in range(0, len(alert)):
            code = 'alert(\''.join(str(alert[i]) + '\');\n')
            mystr = mystr + code
        html_code = html_code + '\n' + mystr + '</script>' + '\n'
    text = text.split('\n')
    for i in range(0, len(text)):
        if not '#title#' or '#head#' in str(text[i]):
            html_code = html_code + '<p>text</p>\n'.replace('text', str(text[i]))
        elif '#title#' in str(text[i]):
            text = text.replace('#title#', '')
            html_code = html_code + '<title>TITLE</title>\n'.replace('TITLE', str(text[i]))
        else:
            text = text.replace('#head#', '')
            html_code = html_code + '<h>txt</h>\n'.replace('txt', str(text[i]))
    return html_code

                                                            
        
