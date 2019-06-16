# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import pafy

SEARCH_URL = 'https://www.youtube.com/results?sp=EgIQAQ%253D%253D&q='
YOUTUBE_URL = "http://youtube.com/watch?v="

def __query(artist, title):
    if artist is not None:
        return "{0} - {1}".format(str(artist), str(title))
    return str(title)

def __isvideo(result):
    if (result.find("channel") is not None 
        or "yt-lockup-channel" in result.parent.attrs["class"] 
        or "yt-lockup-channel" in result.attrs["class"] 
        or "yt-lockup-playlist" in result.parent.attrs["class"] 
        or result.find("googleads") is not None):
        return False
    return True

def __getsec(timestr):
    if ":" in timestr:
        splitter = ":"
    elif "." in timestr:
        splitter = "."
    else:
        return 0
    v = timestr.split(splitter, 3)
    v.reverse()
    sec = 0
    if len(v) > 0:  
        sec += int(v[0])
    if len(v) > 1:  
        sec += int(v[1]) * 60
    if len(v) > 2: 
        sec += int(v[2]) * 3600
    return sec

def __parse(soupitem):
    if not __isvideo(soupitem):
        return None
    content = soupitem.find("div", class_="yt-lockup-content")
    link    = content.find("a")["href"][-11:]
    title   = content.find("a")["title"]
    try:
        videotime = soupitem.find("span", class_="video-time").get_text()
    except:
        videotime = "0"
    return {
        "link": link,
        "title": title,
        "seconds": __getsec(videotime),
    }

def get_videos(artist, title):
    '''
    Search Youtube Urls.

    Return Array:Object has videoid\title\duration
    '''
    query = __query(artist, title)
    query = urllib.request.quote(query)
    ret   = urllib.request.urlopen(SEARCH_URL + query).read()
    soup  = BeautifulSoup(ret, "html.parser")
    urls  = []
    for item in soup.find_all("div", {"class": "yt-lockup-dismissable yt-uix-tile"}):
        obj = __parse(item)
        if obj is not None:
            urls.append(obj)
    return urls

def get_matchvideo(artist, title, duration):
    '''
    Search Youtube Url by Some Conditions

    Return Object has videoid\title\duration
    '''
    urls  = get_videos(artist, title)
    array = []
    toleranceMax = 20
    tolerance = 10
    while tolerance <= toleranceMax:
        tolerance += 1
        array = list(filter(lambda x: abs(x["seconds"] - duration) <= tolerance,urls,))
        if len(array) > 0:
            return array[0]
    return urls[0]

def get_videoinfo(video):
    url  = YOUTUBE_URL + video['link']
    info = pafy.new(url)
    return info

def get_track_streams(artist, title, duration):
    video = get_matchvideo(artist, title, duration)
    info  = get_videoinfo(video)
    return info.getbestaudio(), info.audiostreams


if __name__ == "__main__":
    import aigpy.netHelper
    array = get_videos(None,'Rolling in the deep')
    info  = get_videoinfo(array[0])
    link = info.getbestaudio()
    aigpy.netHelper.downloadFile(link.url, 'e:\\7\\1.m4a')
    a = 0
    

    

            
