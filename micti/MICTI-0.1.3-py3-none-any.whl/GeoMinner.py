import json
import requests
import urllib.request
import gzip
from bs4 import BeautifulSoup
class GEOMinner:
    def __init__(self,geoID):
        self.geoId=geoID
        self.series,self.platform,self.samples=self.getMetadataFromGEOID()

    def getDownloadLinks(self):
        url="https://www.ncbi.nlm.nih.gov/gds/?term="+str(self.geoId)+"&report=DocSums&format=text"
        GeoIdnnn=self.geoId[:len(self.geoId)-3]+"nnn"
        downloadLinks='geo/series/'+GeoIdnnn+'/'+self.geoId+'/'
        return downloadLinks

    def getSeriesMetadata(self,seriesXML):

        series_status={}
        for series_stat in seriesXML.status.children:
            series_status[series_stat.name]=series_stat.string

        series_info={}
        for sample in seriesXML.children:
            series_info[sample.name]=sample.string

        series_info.update(series_status)

        return series_info


    def getPlatformMetadata(self,platformXML):

        platform_status={}
        for platform_stat in platformXML.status.children:
            platform_status[platform_stat.name]=platform_stat.string

        platform_info={}
        for platform in platformXML.children:
            platform_info[platform.name]=platform.string

        platform_info.update(platform_status)
        #print(platform_info)
        return platform_info

    def getSampleMetadata(self,sample):
        sample_status={}
        for samp_stat in sample.status.children:
            sample_status[samp_stat.name]=samp_stat.string

        channel={}
        for chan_stat in sample.channel.children:
            channel[chan_stat.name]=chan_stat.string

        channel_char={}
        for chan_stat_char in sample.channel.find_all("characteristics"):
            channel[str(chan_stat_char.attrs["tag"])]=chan_stat_char.string

        sample_info={}
        for sample in sample.children:
            sample_info[sample.name]=sample.string


        platforms={}
        for platform in sample.find_all("platform-ref"):
            for j in platform:
                print(j.name)
                platforms[j.name]=j.string
        channel.update(channel_char)
        sample_info.update(sample_status)
        sample_info.update(channel)
        sample_info.update(platforms)

        return sample_info

    def getMetadataFromGEOID(self):

        url="https://ftp.ncbi.nlm.nih.gov/"+self.getDownloadLinks()+"miniml/"+self.geoId+"_"+"family.xml.tgz"
        r=urllib.request.urlopen(url)
        rd = gzip.decompress(r.read())
        data=BeautifulSoup(rd,"html5lib")
        #print(data.sample.channel.find("characteristics").attrs["tag"])
        samples={}
        for sample in data.find_all("sample"):#.children:
            #print(sample)
            samples[sample.get("iid")] =self.getSampleMetadata(sample)
            samples[sample.get("iid")]["series_accsesion"]=self.geoId

            for i in sample.find_all("relation"):
                if i.get("type")=="BioSample":
                    #print(i.get("target")+"?report=full&format=text")
                    samples[sample.get("iid")]["biosampleLink"]=i.get("target")+"?report=full&format=text"
                elif i.get("type")=="SRA":
                    samples[sample.get("iid")]["SRALink"]=i.get("target")+"&report=FullXml"


        series={}
        for serie in data.find_all("series"):#.children:
            #series[serie.get("iid")] =self.getSeriesMetadata(serie)
            series =self.getSeriesMetadata(serie)
            #series[sample.get("iid")]["series_accsesion"]=GEOID
        platforms={}
        for platform in data.find_all("platform"):#.children:
            #platforms.self.getPlatformMetadata(platform)
            if platform.get("iid") not in list(platforms.keys()):
                platforms[platform.get("iid")]=(self.getPlatformMetadata(platform))

        print(platforms)

        return series, platforms, samples
    def getSamples(self):
        return self.samples
    def getPlatform(self):
        return self.platform
    def getSeries(self):
        return self.series
