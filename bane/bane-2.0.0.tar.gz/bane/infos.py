import requests,urllib,socket,random,time,re,threading
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
def whois(u,timeout=10,logs=True,returning=False):
 u=u.replace('www.','')
 if logs==True:
  print("[*]Fetching information from https://www.whois.com ...")
 a=''
 try:
  r=requests.get('https://www.whois.com/whois/'+u,headers = {'User-Agent': random.choice(ua)},timeout=timeout).text
  a= r.split('Raw Whois Data</div><pre class="df-raw" id="registrarData">')[1].split('</pre>')[0]
 except:
  pass
 if logs==True:
  print (a.strip())
 if returning==True:
  return a.strip()
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
def headers(u,timeout=10,logs=True,returning=False,proxy=None):
 try:
   s=requests.session()
   a=s.get(u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=timeout).headers
 except Exception as ex:
   return None
 if logs==True:
  for x in a:
   print("{} : {}".format(x,a[x]))
 if returning==True:
  return a
def reverseiplookup(u,timeout=10,logs=True,returning=False,proxy=None):
 '''
   this function is for: reverse ip look up
 '''
 if proxy:
  proxy={'http':'http://'+proxy}
 a=''
 try:
  name, alias, addresslist = socket.gethostbyaddr(u)
  a+=name
 except Exception as e:
  try:
   a+=requests.get("https://api.hackertarget.com/reverseiplookup/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=timeout).text
  except Exception as ex:
   pass
 if logs==True:
  print(a)
 if returning==True:
  return a.strip()
'''
   end of the information gathering functions using: api.hackertarget.com
'''
def dnslookup(u,logs=True,returning=False): #DNS lookup
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
    if (('.' in x) or (':' in x)) and (x not in i):
     if logs==True:
      print (x)
     i.append(x)
 except:
   pass
 if returning==True:
  return i
class scanp(threading.Thread):
 def run (self):
        global portlist
        p=por[flag2]
        s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        r = s.connect_ex((target, p))
        if r == 0:
         portlist.update({p:"Open"})
        else:
         portlist.update({p:"Closed"})
        s.close()
def portscan(u,ports=[21,22,23,25,43,50,80,443,2082,3306],maxtime=5):
 global flag2
 global portlist
 global timeout
 timeout=maxtime
 global por
 por=ports
 global target
 target=u
 for x in range(len(por)):
   flag2=x
   scanp().start()
   time.sleep(.001)
 while(len(portlist)!=len(ports)):
  time.sleep(.1)
 return portlist
