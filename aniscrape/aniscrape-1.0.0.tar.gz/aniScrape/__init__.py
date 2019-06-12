import requests, re, json

def scrape(id,lang="de",upload=False):

	if lang == "en":
		langWeb = "com"
	else:
		langWeb = "de"
	website = requests.get("https://www.anisearch."+langWeb+"/anime/" + str(id))
	if website.status_code != 200:
		return {"id":id,"error":True}
	else:
		dict = {"id":id,"error":False}
		sc = website.text
	
	#Japanese
	try:
		dict["jap"] = re.findall('<img src="https:\/\/cdn\.anisearch\.(?:com|de)\/media\/country\/(?:ja|hk|id|my|kp|ph|sg|kr|tw|th|vn|cn)\.png" class="flag" alt="(?:Japanisch|Japanese|Hong Kong|Indonesien|Indonesia|Malaysia|Nordkorea|North Korea|Philippinen|Philippines|Singapur|Singapore|Südkorea|South Korea|Taiwan|Thailand|Vietnam|China)" title="(?:Japanisch|Japanese|Hong Kong|Indonesien|Indonesia|Malaysia|Nordkorea|North Korea|Philippinen|Philippines|Singapur|Singapore|Südkorea|South Korea|Taiwan|Thailand|Vietnam|China)"> <strong>(.*?)<\/strong>',sc)[0]
	except:
		dict["jap"] = None
		
	#Kanji
	try:
		dict["kan"] = re.findall('<img src="https:\/\/cdn\.anisearch\.(?:com|de)\/media\/country\/(?:ja|hk|id|my|kp|ph|sg|kr|tw|th|vn|cn)\.png" class="flag" alt="(?:Japanisch|Japanese|Hong Kong|Indonesien|Indonesia|Malaysia|Nordkorea|North Korea|Philippinen|Philippines|Singapur|Singapore|Südkorea|South Korea|Taiwan|Thailand|Vietnam|China)" title="(?:Japanisch|Japanese|Hong Kong|Indonesien|Indonesia|Malaysia|Nordkorea|North Korea|Philippinen|Philippines|Singapur|Singapore|Südkorea|South Korea|Taiwan|Thailand|Vietnam|China)"> <strong>.*?<\/strong> <div class="grey">(.*?)<\/div><\/div>',sc)[0]
	except:
		dict["kan"] = None
		
	#English
	try:
		dict["eng"] = re.findall('<img src="https:\/\/cdn\.anisearch\.(?:com|de)\/media\/country\/en.png" class="flag" alt="(?:Englisch|English)" title="(?:Englisch|English)"> (?:<span class="speaker" title="Synchronisiert"><\/span> |<span class="speaker" title="Synchronized"><\/span> )?<strong>(.*?)<\/strong><\/div>',sc)[0]
	except:
		dict["eng"] = None
	#German
	try:
		dict["ger"] = re.findall('<img src="https:\/\/cdn\.anisearch\.(?:com|de)\/media\/country\/de.png" class="flag" alt="(?:Deutsch|German)" title="(?:Deutsch|German)"> (?:<span class="speaker" title="Synchronisiert"><\/span> |<span class="speaker" title="Synchronized"><\/span> )?<strong>(.*?)<\/strong><\/div>',sc)[0]
	except:
		dict["ger"] = None
		
	#Synonyms
	try:
		synonymsUnsplitted = re.findall('<img src="https:\/\/cdn\.anisearch\.(?:com|de)\/media\/country\/xx\.png" class="flag" alt="xx"> (?:Synonyms|Synonyme)<\/div>(.*?)(?:<\/span>)?<\/li>',sc)[0]
		synonymsSplitted = re.split(', <span class="grey">|</span>, ',synonymsUnsplitted)
		dict["syn"] = synonymsSplitted
	except:
		dict["syn"] = None
	
	desc = re.findall('<span itemprop="description" lang="(?:de|en)" id="desc-(?:de|en)" class="desc-zz textblock">(.*?)<\/span>',sc)
	if len(desc) > 0:
		desc = desc[0]
		desc.replace("<br />","\n")
		desc = re.sub("\<.*?\>", '',desc)
		dict["description"] = desc
	else:
		dict["description"] = None
	
	
	#Typ
	try:
		type = re.findall('<li><span>(?:Typ|Type)<\/span>(.*?)<\/li>',sc)[0]
		if type == "Unknown" or type == "Unbekannt":
			dict["type"] = None
		else:
			dict["type"] = type
	except:
		dict["type"] = None
	#Time
	try:
		dict["time"] = re.findall('datetime=".*?">(\d*)min<\/time>',sc)[0]
	except:
		dict["time"] = None
	#Episodes
	try:
		eps = re.findall('<span>(?:Episoden|Episodes)<\/span>(.*?)(?: |<\/li>)',sc)[0]
		if ">?<" in eps:
			dict["episodes"] = None
		else:
			dict["episodes"] = eps
	except:
		dict["episodes"] = None
	#Date
	dict["date"] = {}
	try:
		date = re.findall('<meta itemprop="dateCreated" content="(.*?)">',sc)[0]
		date = date.split("-")
		if date[0] != "0000":
			dict["date"]["year"] = date[0]
		else:
			dict["date"]["year"] = None
		if date[1] != "00":
			dict["date"]["month"] = date[1]
		else:
			dict["date"]["month"] = None
		if date[2] != "00":
			dict["date"]["day"] = date[2]
		else:
			dict["date"]["day"] = None
	except:
		dict["date"]["year"] = None
		dict["date"]["month"] = None
		dict["date"]["day"] = None
	#Country
	try:
		origin = re.findall('<span>(?:Herkunft|Country of Origin)<\/span>(.*?)<\/li>',sc)[0]
		if ">-<" in origin:
			dict["origin"] = None
		else:
			dict["origin"] = origin
	except:
		dict["origin"] = None
	#Adaption
	try:
		adaption_of = re.findall('<span>(?:Adaptiert von|Adapted From)<\/span>(.*?)<\/li>',sc)[0]
		if ">-<" in adaption_of:
			dict["adaption_of"] = None
		else:
			dict["adaption_of"] = adaption_of
	except:
		dict["adaption_of"] = None
	#TargetGroup
	try:
		targetgroup = re.findall('<span>(?:Zielgruppe|Target Group)<\/span>(.*?)<\/li>',sc)[0]
		if ">-<" in targetgroup:
			dict["targetgroup"] = None
		else:
			dict["targetgroup"] = targetgroup
	except:
		dict["targetgroup"] = None
		
	
	dict["genres"] = {}
	#Main Genre
	genre_main = re.findall('href="anime\/genre\/main\/.*?\" class=\"gg showpop\" data-tooltip=\".*?\">(.*?)<\/a><\/li>',sc)
	for i in range(len(genre_main)):
		genre_main[i] = genre_main[i].replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;","\"").replace("&nbsp;"," ").replace("\/","/").replace("&#039;","\'")
	dict["genres"]["genre_main"] = genre_main
	
	#Sub Genre
	genre_sub = re.findall('href="anime\/genre\/subsidiary\/.*?\" class=\"gc showpop\" data-tooltip=\".*?\">(.*?)<\/a><\/li>',sc)
	for i in range(len(genre_sub)):
		genre_sub[i] = genre_sub[i].replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;","\"").replace("&nbsp;"," ").replace("\/","/").replace("&#039;","\'")
	dict["genres"]["genre_sub"] = genre_sub
	
	#Tags
	tags = re.findall('href="anime\/index\/.*?\" class=\"gt showpop\" data-tooltip=\".*?\">(.*?)<\/a><\/li>',sc)
	for i in range(len(tags)):
		tags[i] = tags[i].replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;","\"").replace("&nbsp;"," ").replace("\/","/").replace("&#039;","\'")
	dict["genres"]["tags"] = tags
	
	#Img
	link = re.findall('<figure id="cover-container"><img itemprop="image" src="(.*?)" alt=".*?" title=".*?" id="details-cover">',sc)[0]
	if link.endswith("/0.jpg") or link.endswith("/ecchi.v1.jpg") or link.endswith("/hentai.v1.jpg"):
		dict["img"] = None
	else:
		dict["img"] = link
		
	#hoster
	if upload != False:
		if dict["img"] == None:
			dict["hoster"] = None
		elif upload == "imgur":
			imgurReply = json.loads(requests.post("https://api.imgur.com/3/upload",headers={"Authorization":"Client-ID 54a331a8b74a2ea"},data={"image":link,"type":"url"}).text)
			dict["hoster"] = imgurReply["data"]["link"]
		elif upload == "imgbb":
			try:
				import time
				s = requests.session()
				getAuthToken = s.get("https://imgbb.com/").text
				authToken = re.findall('PF\.obj\.config\.auth_token="(.*?)";',getAuthToken)[0]
				linkDict = json.loads(s.post("https://imgbb.com/json",data={"source":link,"type":"url","action":"upload","timestamp":str(int(time.time())),"auth_token":authToken}).text)
				dict["hoster"] = linkDict["image"]["url"]
			except:
				raise
				dict["hoster"] = "imgbb_error"
		else:
			dict["hoster"] = None
	else:
		dict["hoster"] = None
	
	return dict
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	