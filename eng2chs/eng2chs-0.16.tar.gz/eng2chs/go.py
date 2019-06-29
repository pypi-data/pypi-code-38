# -*- coding:utf-8 -*-
import cgitb
import urllib.request
import urllib.error
import execjs
import re
import time
from eng2chs import readip
from eng2chs import getip
import requests
import socket

cgitb.enable()

'''
主要功能类为tfunction。
使用时在顶端添加 from m_trans import tfunction
建立tfunction实例,使用trans函数,输入参数为需要翻译的内容。
返回结果即为翻译结果。

    exp:    


'''


class Py4Js:
    def __init__(self):
        self.ctx = execjs.compile("""
        function TL(a) {
        var k = "";                                                                                                                                                                         
        var b = 406644;
        var b1 = 3293161072;

        var jd = ".";
        var $b = "+-a^+6";
        var Zb = "+-3^+b+-f";

        for (var e = [], f = 0, g = 0; g < a.length; g++) {
            var m = a.charCodeAt(g);
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
            e[f++] = m >> 18 | 240,
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
            e[f++] = m >> 6 & 63 | 128),
            e[f++] = m & 63 | 128)
        }
        a = b;
        for (f = 0; f < e.length; f++) a += e[f],
        a = RL(a, $b);
        a = RL(a, Zb);
        a ^= b1 || 0;
        0 > a && (a = (a & 2147483647) + 2147483648);
        a %= 1E6;
        return a.toString() + jd + (a ^ b)
    };

    function RL(a, b) {
        var t = "a";
        var Yb = "+";
        for (var c = 0; c < b.length - 2; c += 3) {
            var d = b.charAt(c + 2),
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
        }
        return a
    }
    """)

    def getTk(self, text):
        return self.ctx.call("TL", text)


class tfunction():
    def trans(self, temp, pro = 1, mode = 'e2c'):
        if type(temp) != str:
            return 'content should be str'

        js = Py4Js()
        reobj0 = re.compile(r'^\n',
                            re.M)
        ResultList = reobj0.split(temp)
        temp = ''
        for i in range(len(ResultList)):
            temp += re.sub(r'\n', " ", ResultList[i])
            temp += '\r\n\r\n'
        origin = 0
        last = 0
        String = ''
        i = -1
        k = 0
        n = 0
        result = [""] * (round(len(temp) / 1200) + 1)
        while i < len(temp):
            i += 1
            if i != len(temp):
                if temp[i] == '.' or temp[i] == '?':
                    if i - last < 1200:
                        origin = i
                        continue
                    else:
                        i = origin
                        content = temp[last:origin]
                        last = origin
                else:
                    if i - last >= 1200:
                        i = origin
                        content = temp[last:origin]
                        last = origin
                    else:
                        continue
            else:
                content = temp[last:len(temp)]
            tk = js.getTk(content)
            content = urllib.parse.quote(content)
            socket.setdefaulttimeout(20)

            if mode == 'e2c':
                url = "https://translate.google.cn/translate_a/single?client=t" \
                  "&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca" \
                  "&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1" \
                  "&srcrom=0&ssel=0&tsel=0&kc=2&tk=%s&q=%s" % (tk, content)

            elif mode == 'c2e':
                url = "https://translate.google.cn/translate_a/single?client=t" \
                     "&sl=zh-CN&tl=en&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca" \
                     "&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&ssel=0" \
                     "&tsel=3&kc=2&tk=%s&q=%s" % (tk, content)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
            proxies = readip.readip()
            try:
                if pro == 1:
                    try:
                        requests.adapters.DEFAULT_RETRIES = 5
                        response = requests.get(url=url, headers=headers, allow_redirects = False, proxies = proxies,timeout = 2)
                        print('mode-proxy')
                    except:
                        print('超时 重新请求')
                        response = requests.get(url=url, headers=headers, allow_redirects = False, proxies = proxies,timeout = 2)
                        print('mode-proxy')
                else:
                    response = requests.get(url=url, headers=headers, allow_redirects = False)
                if response.status_code == 200:
                    result[k] = response.text
                    k = k + 1

                    response.close()
                if response.status_code == 302:
                    print('302')
                    getip.get_ip()
                    time.sleep(2)
                    return self.trans(temp,pro)

            except urllib.error.URLError as e:
                print(e.reason)
                return self.trans(temp,pro)

            except socket.timeout:
                print("-----socket timout:", url)
                return self.trans(temp,pro)

            except ConnectionAbortedError as e:
                print(e)
                return self.trans(temp,pro)
            except requests.exceptions.ProxyError as e:
                print(e)
                return self.trans(temp,pro)
            except requests.exceptions.SSLError as e:
                print(e)
                return self.trans(temp,pro)
            except:
                print('unknown error')
                return self.trans(temp,pro)
        return result[0].split('","')[0].replace('[','').replace('"','')