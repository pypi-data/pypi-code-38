def load_cookies_file(filename):
	from http.cookiejar import Cookie, MozillaCookieJar
	ns_cookiejar = MozillaCookieJar()
	ns_cookiejar.load(filename, ignore_discard=True, ignore_expires=True)
	return ns_cookiejar
def load_cookies_string(string):
	from http.cookiejar import Cookie, MozillaCookieJar
	import os, random
	cookieFile = "_cookie_"+str(random.randint(1000000,9999999))
	
	writeCookie = open(cookieFile,"w",encoding="utf8")
	writeCookie.write(string)
	writeCookie.close()
	
	ns_cookiejar = MozillaCookieJar()
	ns_cookiejar.load(string, ignore_discard=True, ignore_expires=True)
	os.remove(cookieFile)
	return ns_cookiejar
