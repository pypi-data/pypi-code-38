import requests,random
from bane.payloads import ua
def wpadmin(u,path='/xmlrpc.php',username='',password='',timeout=10,proxy=None):
 '''
   this function is to check the wordpress given logins using the xmlrpc.php file. if they are correct it returns True, else False
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 if u[len(u)-1]=='/':
  u=u[0:len(u)-1]
 s=False
 u+=path
 post ="""<methodCall>
<methodName>wp.getUsersBlogs</methodName>
<params>
<param><value>{}</value></param>
<param><value>{}</value></param>
</params>
</methodCall>""".format(username,password)
 try:
  r = requests.post(u, data=post,headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if "isAdmin" in r.text:
   s=True
 except:
  pass
 return s
def wpusers(u,path='/wp-json/wp/v2/users',timeout=10,boolean=False,link=False,content=True,proxy=None):
 '''
   this function is to get WP users
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 if u[len(u)-1]=='/':
  u=u[0:len(u)-1]
 s=''
 c=''
 b=False
 u+=path
 try:
  r=requests.get(u, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if ('{"id":'in r.text) and('"name":"' in r.text):
   s+=u
   b=True
   c=r.text
 except Exception as e:
  pass
 if link==True:
  return s
 if boolean==True:
  return b
 if content==True:
  return c
def wpuser(u,path='/wp-json/wp/v2/users/',user=1,timeout=10,boolean=False,link=False,content=True,proxy=None):
 '''
   this function is to return all informations about a WP user with a given index integer
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 if u[len(u)-1]=='/':
  u=u[0:len(u)-1]
 s=''
 c=''
 b=False
 u+=path+str(user)
 try:
  r=requests.get(u, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if ('{"id":'in r.text) and('"name":"' in r.text):
   s+=u
   b=True
   c+=r.text
 except Exception as e:
  pass
 if link==True:
  return s
 if boolean==True:
  return b
 if content==True:
  return c
def wpposts(u,path='/wp-json/wp/v2/posts',timeout=10,boolean=False,link=False,content=True,proxy=None):
 '''
   this function is to get WP posts
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 if u[len(u)-1]=='/':
  u=u[0:len(u)-1]
 s=''
 c=''
 b=False
 u+=path
 try:
  r=requests.get(u, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if ('{"id":'in r.text) and('"date":"' in r.text):
   s+=u
   b=True
   c+=r.text
 except Exception as e:
  pass
 if link==True:
  return s
 if boolean==True:
  return b
 if content==True:
  return c
def wppost(u,path='/wp-json/wp/v2/posts/',post=1,timeout=10,boolean=False,link=False,content=True,proxy=None):
 '''
   this function is to return all informations about a WP post with a given index integer
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 if u[len(u)-1]=='/':
  u=u[0:len(u)-1]
 s=''
 c=''
 b=False
 u+=path+str(post)
 try:
  r=requests.get(u, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout)
  if ('{"id":'in r.text) and('"date":"' in r.text):
   s+=u
   b=True
   c+=r.text
 except Exception as e:
  pass
 if link==True:
  return s
 if boolean==True:
  return b
 if content==True:
  return c
