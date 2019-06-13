import requests,re,random
from bs4 import BeautifulSoup
from payloads import *
def subdomains(u,timeout=10,user_agent=None,proxy=None):
 lit=[]
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 if proxy:
  proxy={'http':'http://'+proxy}
 try:
  r=requests.get('https://findsubdomains.com/subdomains-of/'+u,timeout=timeout).text
  soup = BeautifulSoup(r,"html.parser")
  for a in soup.find_all('table'):
   for x in a.find_all('a'):
    x=str(x)
    if '"/subdomains-of/' in x:
     x=x.split('">')[1].split('<')[0]
     lit.append(x)
 except:
  pass
 return lit
