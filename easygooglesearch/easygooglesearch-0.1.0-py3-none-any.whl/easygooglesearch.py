import requests
import bs4

class Error(Exception):
	pass

class NetworkError(Error):
	pass

class DecodeError(Error):
	pass
def __init__():
	pass
def reverse_gimage(imagelink : str):
	try:
		redirURL = "https://images.google.com/searchbyimage?image_url=" + imagelink
		final = requests.get(redirURL, headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})
	except:
		raise NetworkError("couldn't get webpage from Google")
	try:
		soup = bs4.BeautifulSoup(final.text, 'html.parser')
		rawoutput = soup.findAll('a', attrs={'class':'fKDtNb'})
		output = []
	except:
		raise DecodeError("failed to decode properly. improper or unexpected data was likely supplied. updating this module may fix this")
	for x in rawoutput:
		output.append(x.get_text())
	if output == "[]":
		#return("gosh darn\n\n" + str(soup)[50:] + "\n\n...etc., etc.")
		raise DecodeError("failed to decode properly. improper or unexpected data was likely supplied. updating this module may fix this")
	return(output)

def reverse_gimage_link(imagelink : str):
	return("https://images.google.com/searchbyimage?image_url=" + str(imagelink))

def get_autocomplete_entry(query : str):
	try:
		url = "http://suggestqueries.google.com/complete/search?client=firefox&q=" + query.replace('+', '%2B').replace(' ', '+')
		final = requests.get(url, headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})
	except:
		raise NetworkError("couldn't get webpage from Google")
	try:
		return(final.json()[1])
	except:
		raise DecodeError("failed to decode properly. improper or unexpected data was likely supplied. updating this module may fix this")
