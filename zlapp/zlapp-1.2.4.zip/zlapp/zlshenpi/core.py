from bs4 import BeautifulSoup 
# 横向
def ext_tb1(table):
    soup=BeautifulSoup(table,'html.parser')

    trs=soup.find_all('tr')
    d={}
    for tr in trs:
        tds=tr.find_all('td')
        for i in range(int(len(tds)/2)):
            k,v=tds[2*i].text.strip(),tds[2*i+1].text.strip()
            d[k]=v
    return d

def ext_tb2(table):
    soup=BeautifulSoup(table,'html.parser')

    trs=soup.find_all('tr')
    txtarr=[  [td.text.strip() for td in tr.find_all('td')]  for tr in trs  ]
    d={}
    for i in range(int(len(txtarr)/2)):
        ks=txtarr[2*i]
        vs=txtarr[2*i+1]
        for k,v in zip(ks,vs):
            d[k]=v

    return d
