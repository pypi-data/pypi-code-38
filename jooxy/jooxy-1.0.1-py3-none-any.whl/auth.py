from .config import Config
from .client import Client
from .user import User
from .sessions import Sessions
from .utils import *
from datetime import datetime
import requests, json, os

class JooxAuthError(Exception):
    pass

class Jooxy(Config, Client, Sessions, User):

	DEFAULT_PARAMS 	= dict(country='id', lang='en')
	isLogin			= False
	cache 			= dict()

	def __init__(self, email=None, password=None, saveData=True, cachePath="data/"):
		self.saveData = saveData
		if email and password:
			self._email = email
			self._password = password
			if cachePath[-1] != '/':
				cachePath += "/"
			if not os.path.isdir(cachePath):
				os.makedirs(cachePath)
			self._cachePath = cachePath
			self.isLogin	= True
			self.getUserInfo()

	def isSessionExpired(self, userInfo):
		now = datetime.today()
		expiredTime = "".join(userInfo["expire_time"].split()[
			1:]).replace("GMT", "")
		expireSession = datetime.strptime(expiredTime, "%d%b%Y%H:%M:%S")
		return expireSession <= now

	def getCachedUserInfo(self):
		if self.saveData:
			with open("{}{}.json".format(self._cachePath, self._email.split("@")[0])) as f:
				userInfo = json.loads(f.read())
		else:
			userInfo = self.cache
		if "expire_time" in userInfo:
			if self.isSessionExpired(userInfo):
				log("Session key is expired, trying to re-login..")
				if self.saveData:
					os.remove("{}{}.json".format(
						self._cachePath, self._email.split("@")[0]))
				else:
					self.cache = dict()
				log("Removing old user info..")
				return self.getUserInfo()
			return userInfo
		return None

	def _saveUserInfo(self, userInfo):
		try:
			if self.saveData:
				with open("{}{}.json".format(self._cachePath, self._email.split("@")[0]), "w") as f:
					f.write(json.dumps(userInfo, indent=4))
					log("User info file has been saved!")
					log("Welcome {}".format(userInfo['nickname']))
			else:
				self.cache.update(userInfo)
				log("User info has been saved in sessions!")
				log("Welcome {}".format(userInfo['nickname']))
		except IOError:
			log("Failed to save user info")

	def getUserInfo(self):
		if self.cache != {}:
			return self.getCachedUserInfo()
		if os.path.exists("{}{}.json".format(self._cachePath, self._email.split("@")[0])):
		    return self.getCachedUserInfo()
		newPassword = encryptPassword(self._password)
		params = dict(callback="callBackEmailAuth", authtype=2,
		              wxopenid=self._email, password=newPassword)
		params.update(self.DEFAULT_PARAMS)
		r = requests.get(self.JOOX_API_DOMAIN + self.JOOX_AUTH_PATH, params=params)
		if r.status_code != 200:
		    raise JooxAuthError(r.reason)
		userInfo = json.loads(parseJSONP(r.text))
		if "nickname" in userInfo:
		    self._saveUserInfo(userInfo)
		    return userInfo
		return None