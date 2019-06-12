

from collections import defaultdict

dict1 = [
{'url': 'http://www.banketto.co.uk/banks/online-bank/saga.html', 
'address': 'personal.finance@saga.co.uk'}, 
{'url': 'http://www.sagacareers.co.uk/working-here/support-for-disabled/', 
'address': 'human.resources@saga.co.uk'}, 
{'url': 'http://www.edinburgh.gov.uk/directory_record/261228/saga', 
'address': 'edinburgh@saga.co.uk'}, 
{'url': 'http://www.sellingtravel.uk/in-the-news-reader/january-shopping-incentive-from-saga', 
'address': 'incentives@saga.co.uk'}, 
{'url': 'http://www.chelwest.nhs.uk/about-us/news/news-archive/2006/saga-healthcare-unveils-list-of-best-nhs-hospitals-for-treatment', 
'address': 'angela.clifton@saga.co'}, 
{'url': 'https://www.moneywise.co.uk/news/2011-05-23/elderly-care-costs-to-double-2050', 
'address': 'enquiries@saga.co.uk'}] 

dict3 = [{'url': 'https://account.saga.co.uk/auth6/secureauth.aspx', 
'address': 'mysaga@saga.co.uk'}, 
{'url': 'https://twitter.com/SagaUK', 
'address': 'socialmedia@saga.co.uk'}, 
{'url': 'http://allissaga.co.uk/', 
'address': 'sales@allissaga.co.uk'}, 
{'url': 'https://www.sega.com/', 
'address': 'help@sega.com'}, 
{'url': 'http://www.saga-shipping.dk/', 
'address': 'saga@saga-shipping.dk'}, 
{'url': 'https://www.saga.co.uk/mysaga/', 
'address': 'mysaga@saga.co.uk'}] 

dict2 = [{'url': 'https://twitter.com/sagauk', 
'address': 'socialmedia@saga.co.uk'}, 
{'url': 'https://www.saga-magazine.co.uk/footer/contact/', 
'address': 'subs.enquiries@saga.co.uk'}, 
{'url': 'http://www.gtacredithire.com/acromas-insurance-co-ltd-formerly-saga-insurance/', 
'address': 'claimsdocumentation@saga.co.uk'}, 
{'url': 'http://www.travelweekly.co.uk/atas/directory/18/saga-holidays', 
'address': 'agencysales@saga.co.uk'}, 
{'url': 'http://www.travelweekly.co.uk/atas/directory/18/saga-holidays', 
'address': 'sonja.howell@saga.co.uk'}, 
{'url': 'https://www.towergate.co.uk/Files/f3c5046c-6e96-4359-8995-33a75a8312ef.pdf', 
'address': 'dda@saga.co.uk'}, 
{'url': 'http://directory.email-verifier.io/ben-day-saga-plc-email-company-12230219-477706.html', 
'address': 'ben.day@saga.co.uk'}, 
{'url': 'http://directory.email-verifier.io/ben-day-saga-plc-email-company-12230219-477706.html', 
'address': 'day@saga.co.uk'}, 
{'url': 'http://otp.investis.com/clients/uk/saga_limited/rns/regulatory-story.aspx?cid=852&newsid=943521', 
'address': 'mark.watkins@saga.co.uk'}, 
{'url': 'https://www.glassdoor.co.uk/Reviews/Employee-Review-Saga-Group-RVW18352140.htm', 
'address': 'saga.careers@saga.co.uk'}, 
{'url': 'https://www.prweek.com/article/783814/media-analysis-young-heart-full-life', 
'address': 'melody.rousseau@saga.co.uk'}, 
{'url': 'https://contactcustomerserviceuk.co.uk/company/saga/', 
'address': 'relations@saga.co.uk'}, 
{'url': 'https://www.saga-magazine.co.uk/footer/contact/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjuz6Tl-uXcAhWJ3lQKHb3TBCs4HhAWCB4wAg&usg=AOvVaw3wMp_RzqXU80CrffgRlI4z', 
'address': 'enquiries@saga.co.uk'}, 
{'url': 'http://www.google.comhttp://www.gtacredithire.com/acromas-insurance-co-ltd-formerly-saga-insurance/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjuz6Tl-uXcAhWJ3lQKHb3TBCs4HhAWCEswCg&usg=AOvVaw0teuZB8zvi0MeP8e-zSkwP', 
'address': 'claimsdocumentation@saga.co.uk'}, 
{'url': 'http://www.google.comhttp://www.travelweekly.co.uk/atas/directory/18/saga-holidays&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjuz6Tl-uXcAhWJ3lQKHb3TBCs4HhAWCFEwCw&usg=AOvVaw2JO4oX93YJUYkIppMo9m-v', 
'address': 'agencysales@saga.co.uk'}, 
{'url': 'http://www.google.comhttp://www.travelweekly.co.uk/atas/directory/18/saga-holidays&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjuz6Tl-uXcAhWJ3lQKHb3TBCs4HhAWCFEwCw&usg=AOvVaw2JO4oX93YJUYkIppMo9m-v', 
'address': 'sonja.howell@saga.co.uk'}, 
{'url': 'https://www.towergate.co.uk/Files/f3c5046c-6e96-4359-8995-33a75a8312ef.pdf&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjuz6Tl-uXcAhWJ3lQKHb3TBCs4HhAWCFswDQ&usg=AOvVaw0t8Le5hL-tmWi6KP-7O0Vr', 
'address': 'dda@saga.co.uk'}, 
{'url': 'http://www.google.comhttp://directory.email-verifier.io/ben-day-saga-plc-email-company-12230219-477706.html&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjuz6Tl-uXcAhWJ3lQKHb3TBCs4HhAWCMMBMCQ&usg=AOvVaw3F_3Eog66adWrWiIGyOF-j', 
'address': 'ben.day@saga.co.uk'}, 
{'url': 'http://www.google.comhttp://directory.email-verifier.io/ben-day-saga-plc-email-company-12230219-477706.html&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjuz6Tl-uXcAhWJ3lQKHb3TBCs4HhAWCMMBMCQ&usg=AOvVaw3F_3Eog66adWrWiIGyOF-j', 
'address': 'day@saga.co.uk'}, 
{'url': 'https://contactcustomerserviceuk.co.uk/company/saga/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwjPm6br-uXcAhVnilQKHZSxDRY4MhAWCCMwAw&usg=AOvVaw3yg2idgsM85WV13rvCtYxK', 
'address': 'relations@saga.co.uk'}]



def merge_dicts(*dict_args):
	"""
	Given any number of dicts, shallow copy and merge into a new dict,
	precedence goes to key value pairs in latter dicts.
	"""
	fields = ['url', 'address']
	email_list = [dict(zip(fields, d)) for d in dict_args]		
	
	result = defaultdict(set)
	for dictionary in dict_args:
		if dictionary == '[]':
			pass
		else:
			for d in dictionary:
				for k, v in d.items():  # use d.iteritems() in python 2
					result[k].add(v)				
	
	return result
	
	
		
dict4 = dict1 + dict2 + dict3


data = merge_dicts(dict4)
print(data)
