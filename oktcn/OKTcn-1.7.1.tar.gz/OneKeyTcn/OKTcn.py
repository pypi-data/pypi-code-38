import requests, json, re, time
import NorrisUtils.BuildConfig

API = 'http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long='
url = 'http://www.baidu.com'


# 快速一键短链
def quickOKTcn(url, logfunc=None):
    req = requests.get(API + url, allow_redirects=False)
    jsonDict = json.loads(req.text)
    if logfunc != None:
        # [{'url_short': 'http://t.cn/RmxDsJF', 'url_long': 'http://www.baidu.com', 'type': 0}]
        logfunc(jsonDict)
    try:
        short = jsonDict[0]['url_short']
        long = jsonDict[0]['url_long']
    except:
        return url
    return short


# 文本批量短链
def batchTcn(text, logfunc=None, delay=0):
    results = text
    # pattern = re.compile('http(s)://([\w-]+\.)+[\w-]+(/[\w-./?%&=]*)?')
    pattern = re.compile('[a-zA-z]+://[^\s]*')
    items = re.findall(pattern, text)
    for item in items:
        shortUrl = quickOKTcn(item, logfunc=logfunc)
        if logfunc != None:
            logfunc(item)
            logfunc(shortUrl)
        results = results.replace(item, shortUrl)
        time.sleep(delay)
    if logfunc != None:
        logfunc(results)
    return results


if NorrisUtils.BuildConfig.DebugBackDoor:
    str = '''A、常规签到-京豆
    领京豆 http://t.cn/RdNtSt1
    京东会员 http://t.cn/RpFEyqd
    京豆乐园 http://t.cn/RuLvpAU
    每日福利 http://t.cn/RH151So
    拍拍签到 http://t.cn/R33hjAY
    京豆寻宝 http://t.cn/RdNtStm
    B、常规签到-钢镚
    每日一签 http://t.cn/Rmi1fu9
    打卡领钢镚 http://t.cn/RBUI5aC
    钢镚撒币红包 http://t.cn/R8E5qua
    签到领钢镚 http://t.cn/RTJKaZL
    分享得钢镚 http://t.cn/RdNtSt3
    登录送钢镚 http://t.cn/RTz3v4v
    翻牌赢钢镚 http://t.cn/Rp1dauM
    C、常规签到-小金库
    抢现金红包1 http://t.cn/RuYoe8A
    领京东红包1 http://t.cn/R1EvxPM
    领京东红包2 http://t.cn/RghmZVZ
    红包天天领 http://t.cn/RnWRXmb
    领京东红包3 http://t.cn/Rn5nWKE
    领京东红包4 http://t.cn/RrLCiHy
    领京东红包5 http://t.cn/RrLCacH
    领京东红包6 http://t.cn/RrLCoLR
    抢现金红包2 http://t.cn/RdRyBSu
    抓红包 http://t.cn/REMmS1U
    D、特殊签到
    京豆培育舱 http://t.cn/RHGOTy5
    早起打卡 http://t.cn/R9WTmoL
    智能助理 http://t.cn/R61N6v6
    白条权益中心 http://t.cn/RghmZIl
    白条提额 http://t.cn/RghmZMz
    股票签到 http://t.cn/Rp1dauM
    小金库宝箱 http://t.cn/ROr3fEB'''

    str = '''常规签到-京豆
    领京豆 http://www.baidu.com
    京东会员 http://www.douban.com
    京豆乐园 http://www.jd.com
    每日福利 http://www.taobao.com'''
    batchTcn(text=str, logfunc=print)
