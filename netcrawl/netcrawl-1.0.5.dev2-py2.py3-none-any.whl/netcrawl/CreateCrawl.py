#encoding:utf-8
from netcrawl.BaseCrawl import BaseCrawl

def getBaseCrawler(ip = "127.0.0.1"):
    return BaseCrawl(ip)