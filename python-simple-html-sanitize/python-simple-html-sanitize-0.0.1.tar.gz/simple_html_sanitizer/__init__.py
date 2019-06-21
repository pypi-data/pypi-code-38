# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re


def __mapping_table():
	d = {
		"<u>": "||[u]||",
		"</u>": "||[/u]||",
		"<b>": "||[b]||",
		"</b>": "||[/b]||",
		"<i>": "||[i]||",
		"</i>": "||[/i]||",
		"<br/>": "||[br/]||",
	}
	return d

def __encode_html_string(s):
	d = __mapping_table()
	for k, v in d.items():
		s = s.replace(k, v)
	return s

def __decode_html_string(s):
	d = __mapping_table()
	for k, v in d.items():
		s = s.replace(v, k)
	return s

def sanitize_html(html_str=""):
	encoded_str = __encode_html_string(html_str)
	bs_str = BeautifulSoup(encoded_str, 'html.parser')
	bs_str = bs_str.getText()
	decoded_str = __decode_html_string(bs_str)
	return decoded_str

