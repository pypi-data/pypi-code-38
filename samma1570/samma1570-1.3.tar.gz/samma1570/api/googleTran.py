#   @author: 马朝威 1570858572@qq.com
#   @time: 2019-06-02 12:38


import execjs
from samma1570.spiderTool.myRequest import MyRequest
import requests

class Py4Js():

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


my_request = MyRequest()


def translate(content, f, t):
    url_google = 'http://translate.google.cn/translate_a/single' \
                 '?client=t&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1' \
                 '&pc=1&srcrom=0&ssel=0&tsel=0&kc=2'
    js = Py4Js()
    tk = js.getTk(content)
    values = {'tk': tk, 'q': content, 'sl': f, 'tl': t}
    response = requests.get(url=url_google, params=values).json()
    result_parts = list()
    for tran_sen in response[0]:
        result_parts.append(tran_sen[0])
    result = ''.join(result_parts)
    return result


def translate_my_request(content, f, t):
    url_google = 'http://translate.google.cn/translate_a/single' \
                 '?client=t&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1' \
                 '&pc=1&srcrom=0&ssel=0&tsel=0&kc=2'
    js = Py4Js()
    tk = js.getTk(content)
    values = {'tk': tk, 'q': content, 'sl': f, 'tl': t}
    response = my_request.get(url=url_google, params=values).json()
    result_parts = list()
    for tran_sen in response[0]:
        result_parts.append(tran_sen[0])
    result = ''.join(result_parts)
    return result


if __name__ == '__main__':
    text_tran = translate('你好', 'ch-zn', 'en')







