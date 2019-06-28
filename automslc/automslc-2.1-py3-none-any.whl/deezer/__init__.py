#!/usr/bin/python3
import os,uuid,base64
import requests
from .utils import decryptfile, genurl, calcbfkey
import json

localdir = os.getcwd()
qualities = {"FLAC":{
                     "quality": "9",
                     "extension": ".flac",
                     "qualit": "FLAC"
                    },
             "MP3_320": {
                         "quality": "3",
                         "extension": ".mp3",
                         "qualit": "320"
             },
             "MP3_256": {
                         "quality": "5",
                         "extension": ".mp3",
                         "qualit": "256"
             },
             "MP3_128": {
                         "quality": "1",
                         "extension": ".mp3",
                         "qualit": "128"
             }
            }
header = {"Accept-Language": "en-US,en;q=0.5"}
class TrackNotFound(Exception):
      def __init__(self, message):
          super().__init__(message)
class AlbumNotFound(Exception):
      def __init__(self, message):
          super().__init__(message)
class InvalidLink(Exception):
      def __init__(self, message):
          super().__init__(message)
class BadCredentials(Exception):
      def __init__(self, message):
          super().__init__(message)
class QuotaExceeded(Exception):
      def __init__(self, message):
          super().__init__(message)
class QualityNotFound(Exception):
      def __init__(self, message):
          super().__init__(message)


def request(url, control=False):
    try:
       thing = requests.get(url, headers=header)
    except:
       thing = requests.get(url, headers=header)
    if control == True:
     try:
        if thing.json()['error']['message'] == "no data":
         raise TrackNotFound("Track not found :(")
     except KeyError:
        pass
     try:
        if thing.json()['error']['message'] == "Quota limit exceeded":
         raise QuotaExceeded("Too much requests limit yourself")
     except KeyError:
        pass
     try:
        if thing.json()['error']:
         raise InvalidLink("Invalid link ;)")
     except KeyError:
        pass
    return thing


class Login:
    def __init__(self, mail, password, token=""):
          self.req = requests.Session()
          check = self.get_api("deezer.getUserData")['checkFormLogin']
          post_data = {
                       "type": "login",
                       "mail": mail,
                       "password": password,
                       "checkFormLogin": check
          }
          end = self.req.post("https://www.deezer.com/ajax/action.php", post_data).text
          if "success" == end:
              print("")
              #print("Success, you are in :)")
          else:
              if token == "":
               raise BadCredentials(end + ", and no token provided")
              self.req.cookies["arl"] = token
              if self.req.get("https://www.deezer.com/").text.split("'deezer_user_id': ")[1].split(",")[0] == "0":
               raise BadCredentials("Wrong token :(")

    def get_req(self,url):
        try:
            return self.req.get(url).json()['data']
        except:
            return self.req.get(url).json()['data']

    def get_api(self, method="", api_token="null", json=""):
          params = {
                    "api_version": "1.0",
                    "api_token": api_token,
                    "input": "3",
                    "method": method
          }
          try:
             return self.req.post("http://www.deezer.com/ajax/gw-light.php", params=params, json=json).json()['results']
          except:
             return self.req.post("http://www.deezer.com/ajax/gw-light.php", params=params, json=json).json()['results']

    def download(self, track_id, info_download={}, ip= None, output="/var/www/html/music/download",quality_text='128'):
        track_id=str(track_id)
        try:
            os.makedirs(output)
        except FileExistsError:
            pass
        if ip is None:
            ip = requests.get('https://api.ipify.org').text
        def login():
            self.token = self.get_api("deezer.getUserData")['checkForm']
            return self.get_api("song.getData", self.token, {"sng_id": track_id})
        def get_audio(infos, quality, id,extension):
            try:
                md5 = infos['FALLBACK']['MD5_ORIGIN']
            except KeyError:
                md5 = infos['MD5_ORIGIN']
            hashs = genurl(md5, quality, id, infos['MEDIA_VERSION'])
            try:
                crypt = request("https://e-cdns-proxy-%s.dzcdn.net/mobile/1/%s" % (md5[0], hashs))
            except IndexError:
                raise TrackNotFound("Track not found :(")
            if len(crypt.content) == 0:
                raise TrackNotFound("Error with this track :(")
            file_name=infos['ISRC'] + "_"+track_id+"_"+quality + extension
            path_name = output +"/"+ file_name
            open(path_name, "wb").write(crypt.content)
            decry = open(path_name, "wb")
            decryptfile(crypt.iter_content(2048), calcbfkey(id), decry)
            return "http://{}/{}/{}".format(ip,output.replace("/var/www/html/",""),file_name)
        infos = login()
        while not "MD5_ORIGIN" in str(infos):
            infos = login()
        if int(infos['FILESIZE_FLAC']) > 0  and 'flac' in quality_text:
            quality = "9"
            extension = ".flac"
            try:
                info_download['url_flac']=get_audio(infos,quality,track_id,extension)
            except TrackNotFound:
                info_download['url_flac'] = ""
                pass

        if int(infos['FILESIZE_MP3_320']) > 0  and '320' in quality_text:
            quality = "3"
            extension = ".mp3"
            try:
                info_download['url_320'] = get_audio(infos, quality, track_id,extension)
            except TrackNotFound:
                info_download['url_320'] = ""
                pass
        if int(infos['FILESIZE_MP3_128']) > 0  and '128' in quality_text:
            quality = "1"
            extension = ".mp3"
            try:
                info_download['url_128'] = get_audio(infos, quality, track_id,extension)
            except TrackNotFound:
                info_download['url_128'] = ""
                pass
        info_download['isrc'] = infos['ISRC']
        need = self.get_api("song.getLyrics", self.token, {"sng_id": track_id})
        try:
            info_download['lyric'] = need['LYRICS_TEXT']
        except KeyError:
            info_download['lyric'] = ""
        try:
            info_download['copyright'] = need['LYRICS_COPYRIGHTS']
        except KeyError:
            info_download['copyright'] = ""
        try:
            info_download['lyricist'] = need['LYRICS_WRITERS']
        except KeyError:
            info_download['lyricist'] = ""
        try:
            info_download['lyric_sync'] = json.dumps(need['LYRICS_SYNC_JSON'])
        except KeyError:
            info_download['lyric_sync'] = ""

        return info_download
