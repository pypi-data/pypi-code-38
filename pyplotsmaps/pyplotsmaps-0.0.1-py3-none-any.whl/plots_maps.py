import requests as req
from datetime import datetime


class PLOTSMAPS:
    def __init__(self, API):
        self.link = 'https://iotpibase.herokuapp.com/'
        self.API = API

    def updateMap(self, mapname, latitude, longitude):
        tempLink = self.link + 'updatemap?uuid=' + self.API + '&mapname=' + mapname + '&latitude=' + str(latitude) + '&longitude=' + str(longitude)
        r = req.post(tempLink)
        d = r.json()
        return d

    def updatePlot(self, plotname, ydata):
        tempLink = self.link + 'updateplot' + '?uuid=' + self.API + '&plotx=' + str(datetime.now()) + '&ploty=' + str(ydata) + '&name=' + plotname
        r = req.post(tempLink)
        d = r.json()
        return d
