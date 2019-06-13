import requests,urllib,socket,random,time,re
import bs4
from bs4 import BeautifulSoup
from bane.payloads import *
def info(u,timeout=10,proxy=None):
 '''
   this function fetchs all informations about the given ip or domain using check-host.net and returns them to the use as a list of strings
   with this format:
   'requested information: result'
    
   it takes 2 arguments:
   
   u: ip or domain
   timeout: (set by default to: 10) timeout flag for the request
   usage:
   >>>import bane
   >>>domain='www.google.com'
   >>>bane.info(domain)
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 try:
  h=[]
  u='https://check-host.net/ip-info?host='+u
  c=requests.get(u, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout).text
  soup = BeautifulSoup(c,"html.parser")
  d=soup.find_all("tr")
  for a in d:
   try:
    b=str(a)
    if "IP address" not in b:
     a=b.split('<td>')[1].split('!')[0]
     a=a.split('</td>')[0].split('!')[0]
     c=b.split('<td>')[2].split('!')[0]
     c=c.split('</td>')[0].split('!')[0]
     if "strong" in c:
      for n in ['</strong>','<strong>']:
       c=c.replace(n,"")
     if "<a" in c:
      c=c.split('<a')[0].split('!')[0]
      c=c.split('</a>')[0].split('!')[0]
     if "<img" in c:
      c=c.split('<img')[1].split('!')[0]
      c=c.split('/>')[1].split('!')[0]
     n=a.strip()+': '+c.strip()
     h.append(n)
   except Exception as e:
    pass
 except Exception as e:
  pass
 return h
def nortonrate(u,logs=True,returning=False,timeout=15,proxy=None):
 '''
   this function takes any giving and gives a security report from: safeweb.norton.com, if it is a: spam domain, contains a malware...
   it takes 3 arguments:
   u: the link to check
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning the report as a string format if it is set to: True.
   usage:
   >>>import bane
   >>>url='http://www.example.com'
   >>>bane.nortonrate(domain)
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 s=""
 try:
  if logs==True:
   print('[*]Testing link with safeweb.norton.com')
  ur=urllib.quote(u, safe='')
  ul='https://safeweb.norton.com/report/show?url='+ur
  c=requests.get(ul, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout).text 
  soup = BeautifulSoup(c, "html.parser").text
  s=soup.split("Summary")[1].split('=')[0]
  s=s.split("The Norton rating")[0].split('=')[0]
  if logs==True:
   print('[+]Report:\n',s.strip())
 except:
  pass
 if returning==True:
  return s.strip()
def myip(logs=True,returning=False):
 '''
   this function is for getting your ip using: ipinfo.io
   it takes 2 arguments:   
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning the report as a string format if it is set to: True
   usage:
   >>>import bane
   >>>bane.myip()
   xxx.xx.xxx.xxx
   >>>print bane.myip(returnin=True,logs=False)
   xxx.xxx.xx.xxx
'''
 c=""
 try:
   c+=requests.get("http://ipinfo.io/ip",headers = {'User-Agent': random.choice(ua)} ,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
'''
   functions below are using: api.hackertarget.com services to gather up any kind of informations about any given ip or domain
   they take 3 arguments:
   u: ip or domain
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning the report as a string format if it is set to: True
   general usage:
   >>>import bane
   >>>ip='50.63.33.34'
   >>>bane.dnslookup(ip)
   >>>bane.traceroute(ip)
   >>>bane.nmap(ip)
   etc...
'''
def dnslookup(u,logs=True,returning=False,proxy=None):
 '''
   this function is for: DNS look up
 '''
 if proxy:
  proxy={'http':'http://'+proxy}
 c=''
 try:
  c=requests.get("https://api.hackertarget.com/dnslookup/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
def whois(u,logs=True,returning=False,proxy=None):
 '''
   this function is for: whois
 '''
 if proxy:
  proxy={'http':'http://'+proxy}
 c=''
 try:
   c=requests.get("https://api.hackertarget.com/whois/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
def traceroute(u,logs=True,returning=False,proxy=None):
 '''
   this function is for: tracerout
 '''
 c=""
 if proxy:
  proxy={'http':'http://'+proxy}
 try:
   c=requests.get("https://api.hackertarget.com/mtr/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
def reversedns(u,logs=True,returning=False,proxy=None):
 '''
   this function is for: reverse DNS look up
 '''
 c=""
 if proxy:
  proxy={'http':'http://'+proxy}
 try:
   c=requests.get("https://api.hackertarget.com/reversedns/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
def geoip(u,logs=True,returning=False,proxy=None):
 '''
   this function is for getting: geoip informations
 '''
 if proxy:
  proxy={'http':'http://'+proxy}
 c=""
 try:
   c=requests.get("https://api.hackertarget.com/geoip/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
def nmap(u,logs=True,returning=False,proxy=None):
 '''
   this function is for: nmap
 '''
 if proxy:
  proxy={'http':'http://'+proxy}
 c=""
 try:
   c=requests.get("https://api.hackertarget.com/nmap/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
def reverseiplookup(u,logs=True,returning=False,proxy=None):
 '''
   this function is for: reverse ip look up
 '''
 if proxy:
  proxy={'http':'http://'+proxy}
 c=""
 try:
   c=requests.get("https://api.hackertarget.com/reverseiplookup/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=10).text
 except:
  pass
 if logs==True:
  print (c.strip())
 if returning==True:
  return c.strip()
'''
   end of the information gathering functions using: api.hackertarget.com
'''
def ips(u,logs=True,returning=False):
 '''
   this function resolves the domain to all its associated ip addresses
   u: ip or domain
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning the report as a string format if it is set to: True.
   usage:
   >>>import bane
   >>>bane.ips('www.google.com')
   >>>a=bane.ips('www.facebook.com',returning=True)
 '''
 i=[]
 try:
   c= socket.getaddrinfo( u, 80)
   for x in c:
    x= x[4][0]
    if ('.' in x) and (x not in i):
     if logs==True:
      print (x)
     i.append(x)
 except:
   pass
 if returning==True:
  return i
