from lxml import html
import requests

pageHolder = []
pids = []
urls = []
for i in range(94, 99): # Web links change for different categories just in this part
    pageHolder.append(requests.get('http://www12.statcan.gc.ca/nhs-enm/2011/dp-pd/dt-td/Lp-eng.cfm?LANG=E&APATH=3&DETAIL=0&DIM=0&FL=A&FREE=0&GC=0&GID=0&GK=0&GRP=0&PID=0&PRID=0&PTYPE=105277&S=0&SHOWALL=0&SUB=0&Temporal=2013&THEME='+str(i)+'&VID=0&VNAMEE=&VNAMEF='))

for page in pageHolder:
    tree = html.fromstring(page.content)
    pids.append([str.replace(el.attrib['href'],'Download.cfm?','') for el in tree.xpath('//a[starts-with(@href, "Download.cfm?")]')])
    #flatten and add to url
    for i in pids:
        for j in i:
            urls.append('http://www12.statcan.gc.ca/nhs-enm/2011/dp-pd/dt-td/OpenDataDownload.cfm?' + j)

with open('z:/Canadian Census/New_links_for_download.csv', 'a') as file:
    for url in urls:
        file.write(url+'\n')
