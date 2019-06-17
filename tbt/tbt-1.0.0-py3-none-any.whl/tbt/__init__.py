def load_cookies_from_mozilla(filename):
	from http.cookiejar import Cookie, MozillaCookieJar
	ns_cookiejar = MozillaCookieJar()
	ns_cookiejar.load(filename, ignore_discard=True, ignore_expires=True)
	return ns_cookiejar