import requests,random,re
import bs4
from bs4 import BeautifulSoup
from bane.payloads import *
def inputs(u,value=False,timeout=10,user_agent=None,bypass=False,proxy=None):
 '''
   this function is to get the names and values of input fields on a given webpage to scan.

   it takes 4 arguments:

   u: the page's link (http://...)
   value: (set by default to: False) to return the value of the fields set it to:True then the field's name and value will be string of 2 
   values sperated by ":"
   timeout: (set by default to: 10) timeout flag for the request
   bypass: (set by default to: False) to bypass anti-crawlers

  usage:

  >>>import bane
  >>>link='http://www.example.com'
  >>>bane.inputs(link)
  ['email','password','rememberme']
  >>>a=bane.inputs(link,value=True)
  ['email','password','rememberme:yes','rememberme:no']
  
 '''
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 if proxy:
  proxy={'http':'http://'+proxy}
 if bypass==True:
  u+='#'
 l=[]
 try:
  c=requests.get(u, headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
  soup= BeautifulSoup(c,'html.parser')
  p=soup.find_all('input')
  for r in p: 
    v=""
    if r.has_attr('name'):
     s=str(r)
     s=s.split('name="')[1].split(',')[0]
     s=s.split('"')[0].split(',')[0]
     if (r.has_attr('value') and (value==True)):
      v=str(r)
      v=v.split('value="')[1].split(',')[0]
      v=v.split('"')[0].split(',')[0]
    if value==True:
     y=s+":"+v
    else:
     y=s
    if y not in l:
     l.append(y)
 except Exception as e:
  pass
 return l
def forms(u,value=True,user_agent=None,timeout=10,bypass=False,proxy=None):
 '''
   same as "inputs" function but it works on forms input fields only
 '''
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 if proxy:
  proxy={'http':'http://'+proxy}
 if bypass==True:
  u+='#'
 l=[]
 try:
  c=requests.get(u, headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
  soup= BeautifulSoup(c,'html.parser')
  i=soup.find_all('form')
  for f in i:
   p=f.find_all('input')
   for r in p: 
    v=""
    if r.has_attr('name'):
     s=str(r)
     s=s.split('name="')[1].split(',')[0]
     s=s.split('"')[0].split(',')[0]
     if (r.has_attr('value') and (value==True)):
      v=str(r)
      v=v.split('value="')[1].split(',')[0]
      v=v.split('"')[0].split(',')[0]
    if value==True:
     y=s+":"+v
    else:
     y=s
    if y not in l:
     l.append(y)
 except Exception as e:
  pass
 return l
def loginform(u,timeout=10,user_agent=None,bypass=False,value=True,proxy=None):
 '''
   same as "inputs" function but it works on login input fields only
 '''
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 if proxy:
  proxy={'http':'http://'+proxy}
 if bypass==True:
  u+='#'
 l=[]
 try:
  c=requests.get(u, headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
  soup= BeautifulSoup(c,'html.parser')
  i=soup.find_all('form')
  for f in i:
   p=f.find_all('input')
   for r in p: 
    v=""
    if r.has_attr('name'):
     s=str(r)
     s=s.split('name="')[1].split(',')[0]
     s=s.split('"')[0].split(',')[0]
     if (r.has_attr('value') and (value==True)):
      v=str(r)
      v=v.split('value="')[1].split(',')[0]
      v=v.split('"')[0].split(',')[0]
    if value==True:
     y=s+":"+v
    else:
     y=s
    if y not in l:
     l.append(y)
 except Exception as e:
  pass
 return l
def crawl(u,timeout=10,user_agent=None,bypass=False,proxy=None):
 '''
   this function is used to crawl any given link and returns a list of all available links on that webpage with ability to bypass anti-crawlers
   
   the function takes those arguments:
   
   u: the targeted link
   timeout: (set by default to 10) timeout flag for the request
   bypass: (set by default to False) option to bypass anti-crawlers by simply adding "#" to the end of the link :)

   usage:

   >>>import bane
   >>>url='http://www.example.com'
   >>>bane.crawl(url)
   
   >>>bane.crawl(url,bypass=True)
'''
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 if proxy:
  proxy={'http':'http://'+proxy}
 h=[]
 if bypass==True:
  u+='#'
 try:
  c=requests.get(u, headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
  soup = BeautifulSoup(c,"html.parser")
  u=u.split(u.split("/")[3])[0]
  u=u[0:len(u)-1]
  for a in soup.find_all('a'):
   if a.has_attr('href'):
    try:
     a=str(a)
     a=a.split('href="')[1].split('"')[0]
     a=a.split('"')[0].split('"')[0]
     if ("://" not in a) and ('.'not in a):
      if a[0]=="/":
       a=a[1:len(a)]
      a=u+'/'+a
     if (a not in h) and (u in a):
      if (a!=u+"/") and (a!=u):
       h.append(a)
    except Exception as e:
     pass
 except:
  pass
 return h
def pather(u,timeout=10,user_agent=None,bypass=False,proxy=None):
 '''
   this function is similar to the "crawl" function except that it returns only the paths not the full URL.
   
   the function takes those arguments:
   
   u: the targeted link
   timeout: (set by default to 10) timeout flag for the request
   bypass: (set by default to False) option to bypass anti-crawlers by simply adding "#" to the end of the link :)

   usage:

   >>>import bane
   >>>url='http://www.example.com'
   >>>bane.pather(url)
   
   >>>bane.pather(url,bypass=True)
'''
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 if proxy:
  proxy={'http':'http://'+proxy}
 h=[]
 p=[]
 if bypass==True:
  u+='#'
 try:
  c=requests.get(u, headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
  soup = BeautifulSoup(c,"html.parser")
  u=u.split(u.split("/")[3])[0]
  u=u[0:len(u)-1]
  for a in soup.find_all('a'):
   if a.has_attr('href'):
    try:
     a=str(a)
     a=a.split('href="')[1].split('"')[0]
     a=a.split('"')[0].split('"')[0]
     if ("://" not in a) and ('.' not in a):
      if a[0]=="/":
       a=a[1:len(a)]
      a=u+'/'+a
     if (a not in h) and (u in a):
      if (a!=u+"/") and (a!=u):
       h.append(a)
    except Exception as e:
     pass
 except:
  pass
 for x in h:
  p.append(x.split(u)[1])
 return p
def media(u,timeout=10,user_agent=None,bypass=False,proxy=None):
 '''
   this funtion was made to collect the social media links related to the targeted link (facebook, twitter, instagram...).

   the function takes those arguments:
   
   u: the targeted link
   timeout: (set by default to 10) timeout flag for the request
   bypass: (set by default to False) option to bypass anti-crawlers by simply adding "#" to the end of the link :)

   usage:

   >>>import bane
   >>>url='http://www.example.com'
   >>>bane.media(url)
   
   >>>bane.media(url,bypass=True)
'''
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 h=[]
 if proxy:
  proxy={'http':'http://'+proxy}
 try:
  if bypass==True:
   u+='#'
  c=requests.get(u,headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
  soup = BeautifulSoup(c,"html.parser")
  ul=u.split('://')[1].split('"')[0]
  ur=ul.replace("www.",'') 
  for a in soup.findAll('a'):
   try:
    if a.has_attr('href') and (u not in str(a)) and (ur not in str(a)):
     a=str(a)
     a=a.split('href="h')[1].split('"')[0]
     a=a.split('"')[0].split('"')[0]
     a='h'+a
     if a not in h:
      h.append(a)
   except:
    pass
 except:
  pass
 return h
def subdomains(u,timeout=10,user_agent=None,proxy=None):
 '''
   this function collects the subdomains found on the targeted webpage.

   the function takes those arguments:
   
   u: the targeted link
   timeout: (set by default to 10) timeout flag for the request
   bypass: (set by default to False) option to bypass anti-crawlers by simply adding "#" to the end of the link :)

   usage:

   >>>import bane
   >>>domain='example.com'
   >>>bane.subdomains(domain)
'''
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
def subdomains2(u,timeout=10,user_agent=None,bypass=False,proxy=None):
 '''
   this function collects the subdomains found on the targeted webpage.

   the function takes those arguments:
   
   u: the targeted link
   timeout: (set by default to 10) timeout flag for the request
   bypass: (set by default to False) option to bypass anti-crawlers by simply adding "#" to the end of the link :)

   usage:

   >>>import bane
   >>>url='http://www.example.com'
   >>>bane.subdomains(url)
   
   >>>bane.subdomains(url,bypass=True)
'''
 if user_agent:
  us=user_agent
 else:
  us=random.choice(ua)
 if proxy:
  proxy={'http':'http://'+proxy}
 h=[]
 try:
  if bypass==True:
   u+='#'
  c=requests.get(u, headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
  ul=u.split('://')[1].split('"')[0]
  soup = BeautifulSoup(c,"html.parser")
  for a in soup.findAll('a'):
   if a.has_attr('href') and (ul.replace("www",'') in str(a)) and (u not in str(a)):
    a=str(a)
    try:
     a=a.split('://')[1].split('"')[0]
     a=a.split('/')[0].split('"')[0]
     if a not in h:
      h.append(a)
    except Exception as e:
     pass
 except:
  pass
 return h
