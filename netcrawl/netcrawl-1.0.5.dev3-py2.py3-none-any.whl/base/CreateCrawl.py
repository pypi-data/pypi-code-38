#encoding:utf-8
from base.BaseCrawl import BaseCrawl

def getBaseCrawler(ip = "127.0.0.1"):
    return BaseCrawl(ip)