import requests
import re
import json
import os
import random
import traceback
from bs4 import BeautifulSoup


requests.packages.urllib3.disable_warnings()

def baidu(domain):
	"""Return the balance remaining after depositing *amount*
	dollars."""
	
	def url_clean(link):
		response = requests.get(link, headers=headers, proxies=proxy, verify=False)
		url = response.url
		return url
		
	saerchfor = '"@{}"'.format(domain)
	
	proxy = {'http' : 'http://127.0.0.1:8080',
	         'https': 'https://127.0.0.1:8080'}
	
	headers = {"User-Agent" : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
	        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate'}
	emails = []
	for start in range(0,1000,10):
		try:

			link = 'https://www.baidu.com/s?wd={}&pn={}'.format(saerchfor, start)

			if proxy:
				response = requests.get(link, headers=headers, proxies=proxy, verify=False)
			else:
				response = requests.get(link, headers=headers, verify=False)

			
			soup = BeautifulSoup(response.content, "lxml")

			for li in soup.findAll('div', {'id': 'content_left'}):
				if re.search(r'.*?([a-zA-Z0-9.-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*).*?', li.text):
					match = re.search(r'.*?([a-zA-Z0-9.-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*).*?', li.text)
					if domain in match.groups()[0]:
						if li.find('h3', {'class': 't c-title-en'}):
							h = li.find('h3', {'class': 't c-title-en'})
							url =  h.find('a')['href']
							url = url_clean(url)
							emails.append((url, match.groups()[0]))
				
		
		except Exception:			
			print(traceback.print_exc())
	
	print(emails)


domain = 'nccgroup.com'
baidu(domain)
