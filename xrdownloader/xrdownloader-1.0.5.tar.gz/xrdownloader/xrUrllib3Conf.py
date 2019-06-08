# -*-coding: utf8;-*-
try:
 import urllib3
 import certifi
 import sys
except (ImportError,Exception) as e:
 print(e)
 quit()

def xrUrllib3():
  # declare urllib3 module properties and methods
  user_agent = {'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
  http = urllib3.PoolManager(
  cert_reqs='CERT_REQUIRED', 
  ca_certs=certifi.where(),
  headers=user_agent)
  return http

if __name__ == '__main__':
   sys.exit()
