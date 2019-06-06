import os
import numpy as np
import pandas as pd
import itertools
import collections
from telegram.ext import Updater,InlineQueryHandler,CommandHandler
import requests
import re
from telegram import Bot

notigistic_bot=Bot(r'883796622:AAE4eSIVACAIph2l_8124OhilKdRMQMZ1gY')

class TheChat(object):
	
	def __init__(self,chat_id,bot=None):
		self.chat_id=chat_id
		self.bot=bot or notigistic_bot
	
	def send_message(self,message):
		return self.bot.send_message(chat_id=self.chat_id,text=message)
	
	def send_document(self,filepath):
		return self.bot.send_document(chat_id=self.chat_id,document=open(filepath,'rb'))

egistic_notify=TheChat(r'-366778823')

# def get_url():
# 	contents=requests.get('https://random.dog/woof.json').json()
# 	url=contents['url']
# 	return url
#
# def get_image_url():
# 	file_extension=''
# 	url=None
# 	while file_extension not in allowed_extension:
# 		url=get_url()
# 		file_extension=re.search("([^.]*)$",url).group(1).lower()
# 	return url

# def bop(the_bot: Bot,text):
# 	# url=get_image_url()
# 	# the_bot.send_photo(chat_id=chat_id,photo=url)
# 	pass
#
# def egistic_notify_send_text(text):
# 	notigistic_bot.send_message(chat_id=chat_id,text=text)

def main():
	egistic_notify.send_document(r'/home/lgblkb/PycharmProjects/Egistic/Scripts/tut_1.py')
	pass

# updater=Updater(token)
# dp=updater.dispatcher
# dp.add_handler(CommandHandler('bop',bop))
# updater.start_polling()
# updater.idle()

if __name__=='__main__':
	main()
