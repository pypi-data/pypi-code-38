import sys
from datetime import datetime
from base64 import b64encode, b64decode

#: Replace Multiple Values

def replace_multiple(self, dictionary):
	"""
	Replaces multiple items with dictionary keys being the item to replace, and values being replacements.
	>>> replace_multiple('The Apple is Red.', {'Apple': 'Grass', 'Red': 'Green'})
	'The Grass is Green.'
	"""
	t = self
	for k in dictionary:
		t = t.replace(k, dictionary[k])
	return t

#: Format Date

def format_date(self, date_input='mdy', date_format='mmddyy', delimiter=''):
	"""
	Formats date string.
	>>> format_date('1/01/75', date_input='mdy', date_format='mmddyyyy', delimiter='-')
	'01-01-1975'
	>>> format_date('75/01/01', date_input='ymd', date_format='yyyymmdd', delimiter='')
	'19750101'
	>>> format_date('12252019', date_input='mdy', date_format='yymmdd', delimiter='/')
	'19/12/25'
	"""
	date = self
	date = replace_multiple(str(date), {'-': '', '/': '', '.': ''})
	final_date = ''
	if len(date) == 5 or len(date) == 7 and date_input == 'mdy':
		date = '0' + date
	if date_input == 'mdy':
		month = date[:2]
		day = date[2:4]
		year = date[4:]
	elif date_input == 'ymd':
		if len(date) == 8:
			year = date[:4]
			month = date[4:6]
			day = date[6:]
		elif len(date) == 6:
			year = date[:2]
			month = date[2:4]
			day = date[4:]
	if len(year) == 2:
		if int(year) >= 70:
			year = '19' + year
		elif int(year) < 70:
			year = '20' + year
	date_order = {'m': 0, 'd': 0, 'y': 0}
	place_temp = 'N'
	place_order = -1
	for i in range(0, len(date_format)):
		if date_format[i] != place_temp:
			place_order += 1
			place_temp = date_format[i]
			date_order[date_format[i]] = place_order
		else:
			continue
	itt = 0
	while itt < 3:
		for key in date_order:
			if date_order[key] == itt:
				if key == 'm':
					final_date += month[(len(month) - date_format.count(key)):]
				if key == 'd':
					final_date += day[(len(day) - date_format.count(key)):]
				if key == 'y':
					final_date += year[(len(year) - date_format.count(key)):]
				if itt != 2:
					final_date += delimiter
				date_order.pop(key)
				itt = itt + 1
				break
	return final_date

#: Find Nth index of string

def find_nth(self, string, n):
	"""
	Expects containing string, string or char to find, and nth occurence.
	>>> find_nth('apple picking', 'p', 3)
	6
	>>> find_nth('red red iamredgreen', 'red', 3)
	11
	"""
	if len(string) > 1 or ord(string) < sys.maxunicode:
		repl = chr(sys.maxunicode) * len(string)
	else:
		repl = chr(sys.maxunicode - 1)
	return self.replace(string, repl, n - 1).find(string)

#: Base64 Encode String

def b64_encode(self):
	"""
	Expects string, returns Base64-Encoded string
	>>> b64_encode('plain_text')
	'cGxhaW5fdGV4dA=='
	"""
	return b64encode(self.encode()).decode('utf-8')

#: Base64 Decode String

def b64_decode(self):
	"""
	Expects string, returns Base64-Decoded string
	>>> b64_decode('cGxhaW5fdGV4dA==')
	'plain_text'
	"""
	return b64decode(self.encode()).decode('utf-8')

#: Get Date and Time from ISO Date

def get_iso_date(self, iso_format='%Y-%m-%dT%H:%M:%S.%fZ', date_format='mmddyyyy', delimiter='/'):
	"""
	Expects string, returns dict of date info
	>>> get_iso_date('2019-05-27T19:09:04.285211Z')
	{'date': '05/27/2019', 'time': '19:09:04', 'micros': '285211', 'date_and_time': '05/27/2019-19:09:04', 'full_date': '05/27/2019-19:09:04.285211'}
	"""
	date_obj = datetime.strptime(self, iso_format)
	date = format_date(date_obj.strftime('%m%d%Y'), date_format=date_format, delimiter=delimiter)
	time = date_obj.strftime('%H:%M:%S')
	micros = date_obj.strftime('%f')
	return {
		'date': date,
		'time': time,
		'micros': micros,
		'date_and_time': f'{date}-{time}',
		'full_date': f'{date}-{time}.{micros}'
	}

#::: END PROGRAM :::
