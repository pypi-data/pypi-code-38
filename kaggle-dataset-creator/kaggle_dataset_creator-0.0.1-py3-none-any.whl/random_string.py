import random
import base64
from datetime import datetime
from .exceptions import InvalidLengthException, InvalidBooleanException
import re

def data_is_valid(length, shuffle):
	valid, exception = False, None

	if type(length) is not int or type(length) is not int:
		exception = InvalidLengthException
	elif type(shuffle) is not bool:
		exception = InvalidBooleanException
	else:
		valid = True

	return valid, exception


def random_string(length=10, shuffle=True):
	valid, exception = data_is_valid(length, shuffle)
	if not valid:
		raise exception

	now = str(datetime.now())

	enc_now_str = base64.b64encode(now.encode("utf8")).decode("utf8")
	enc_now_str2 = base64.b64encode(enc_now_str.encode("utf8")).decode("utf8")
	enc_now_str3 = base64.b64encode(enc_now_str2.encode("utf8")).decode("utf8")

	if now[-1] in ["6", "1"]:
		r_str = enc_now_str[::-1]
	elif now[-1] in ["7", "2"]:
		r_str = enc_now_str2[::-1]
	elif now[-1] in ["9", "3"]:
		r_str = enc_now_str3[::-1]
	elif now[-1] in ["8", "4"]:
		r_str = enc_now_str3
	else: # '5', '0'
		r_str = enc_now_str

	if shuffle:
		r_str = r_str[::-1]

	# while len(r_str) > length:

	return r_str[:length]

if __name__ == "__main__":
	print(random_string())
	print(random_string())
	print(random_string())

