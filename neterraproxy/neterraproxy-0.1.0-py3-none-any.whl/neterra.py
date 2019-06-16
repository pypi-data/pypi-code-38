#!/usr/bin/python
import requests
import time
import json
import os
import sys

import logging
logger = logging.getLogger("neterra.py")



#to disable warnings related to https certificates verification
import urllib3
urllib3.disable_warnings()

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

from bs4 import BeautifulSoup



class NeterraProxy(object):

    def __init__(self, username, password, app_dir):
        self.username = username
        self.password = password
        #self.cookieJar = cookielib.CookieJar()
        self.session = requests.Session()
        self.expireTime = 0
        self.app_dir = app_dir
        #client 
        script_dir = os.path.dirname(__file__)
        self.channelsJson = json.load(open(script_dir + '/channels.json'))
    

        
    def checkAuthentication(self):
        now = int(time.time() * 1000)
        if now > self.expireTime:
            self.authenticate2()
    
    def authenticate2(self):
        token = ""
        logged = False
        self.session.cookies.clear()
        loginUrl="https://neterra.tv/sign-in"
        try:

            headers = {'User-Agent': 'Mozilla/5.0'}
            r = self.session.get(loginUrl, headers = headers)

            soup = BeautifulSoup(r.content, 'html.parser')
            element = soup.find(attrs={"name" : "_token"})
            token = element["value"]
 
            formBody = {"username": self.username, \
                        "password": self.password, \
                        "_token": token}

            self.session.headers.update({   
            'X-CSRF-TOKEN': '{0}'.format(token),
            })

            r = self.session.post(loginUrl, data = formBody, headers=self.session.headers)
            if r.text.find("\"SIGNED\":true") != -1:
                logged = True
            
        except requests.exceptions.RequestException as err:
            logger.exception("message")
            sys.exit(1)   

        if logged:
            self.expiretime = int(time.time() * 1000) + 28800000
        return logged
    
    def getM3U82(self):
        r = self.session.get('https://www.neterra.tv/live')
        soup = BeautifulSoup(r.content, 'html.parser')
        channelsPlaylistElement = soup.find("ul",{"class" : "playlist-items"})
        
        from io import StringIO
        sb = StringIO()
        sb.write("#EXTM3U\n")

        for li in channelsPlaylistElement.findAll('li', attrs={'class': None}):
            channel = li.find('a', {"class" : "playlist-item"})
            chanName = channel.attrs["title"]
            chanId = li.find("div", {"class" : "js-pl-favorite playlist-item__favorite"}) \
                                    .attrs["data-id"]
            if chanId in self.channelsJson:
                tvgId = self.channelsJson[chanId]["tvg-id"]
                tvgName = self.channelsJson[chanId]["tvg-name"]
                group = self.channelsJson[chanId]["group"]
                logo = self.channelsJson[chanId]["logo"]
                #print chanName + " : " + tvgId
            else:
                tvgId = ""
                tvgName = ""
                group = ""
                logo = ""
                #print chanName + " : not found"
            chdata = "#EXTINF:-1 tvg-id=\"{0}\" tvg-name=\"{1}\" tvg-logo=\"{2}\" group-title=\"{3}\", {4} \n " \
                            .format(tvgId, tvgName,logo, group, chanName)
            link = "http://{0}/playlist.m3u8?ch={1}\n" \
                            .format(self.host, chanId)
            #sb.write(chdata.encode("utf-8"))
            sb.write(chdata)
            sb.write(link)     

        return sb.getvalue().encode()
       

    def __getStream2(self, chanId):
        self.checkAuthentication()
        playUrl = "https://www.neterra.tv/live/play/" + str(chanId)
        sr = self.session.get(playUrl)
        return sr.json()


    def getPlayLink2(self, chanId):
        playLinkJson=self.__getStream2(chanId)
        import json, io
        # with io.open(self.script_dir + '/playLinkJson.json','w',encoding="utf-8") as outfile:
        #      outfile.write(unicode(json.dumps(playLinkJson, ensure_ascii=False)))
        link = playLinkJson["link"]
        #link = playLinkJson["url"]["play"]
        return link




