"""
        Module to convert various data

        11/07/2016 - Created
		02/03/2019 - Converted to make python3 compatible 
        
        def convert_time_from_seconds(seconds_given)
			Converts seconds into minutes/hours. 
		
		def IP2Int(ip)
			Converts an IPv4 address to a interger - This is useful to store IP addresses in databases
		
		def Int2IP(ipnum)
			Converts an interger back to an IPv4 address

		def urlcode(url, encode=False)
			Wrapper for urllib.parse.quote and urllib.parse.unquote.
			From urllib docs - Replace special characters in string using the %xx escape. Letters, digits, 
			and the characters '_.-' are never quoted. By default, this function is intended for quoting 
			the path section of URL. 
			https://docs.python.org/3.1/library/urllib.parse.html?highlight=urllib#urllib.parse.quote

"""
import urllib.parse

version = '1.1'

def convert_time_from_seconds(seconds_given):
	if seconds_given == "N/A":
		return seconds_given
	else:
		m, s = divmod(seconds_given, 60)
		h, m = divmod(m, 60)
		total_time = "%d:%02d:%02d" % (h, m, s)

		return total_time


def IP2Int(ip):
	if '.' in str(ip):
		o = list(map(int, ip.split('.')))
		res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
		return res
	else:
		return ip


def Int2IP(ipnum):
	o1 = int(ipnum / 16777216) % 256
	o2 = int(ipnum / 65536) % 256
	o3 = int(ipnum / 256) % 256
	o4 = int(ipnum) % 256
	return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()


def urlcode(url, encode=False):
	if encode:
		# Convert string to URL safe
		return urllib.parse.quote(url)
	else:
		# Convert string to human readable
		return urllib.parse.unquote(url)
