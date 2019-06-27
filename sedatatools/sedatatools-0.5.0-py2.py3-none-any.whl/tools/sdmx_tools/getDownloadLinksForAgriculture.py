from lxml import html
import requests

page = requests.get('http://www5.statcan.gc.ca/cansim/a03?C2DB=PRD&pattern=0040200..0040242&p2=50&retrLang=eng&CII_SuperBtn=Search&copyVersion=0&lang=eng&typeValue=1')
tree = html.fromstring(page.content)
ids = ['0'+ str.replace(i,'-','') for i in tree.xpath("//td/a/span/text()")]

with open('z:/Canadian Census/Download_links_agriculture.csv', 'w') as file:
    for i in ids:
        file.write('http://www20.statcan.gc.ca/tables-tableaux/cansim/sdmx/{}.zip\n'.format(i))