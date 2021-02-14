import requests
import json
import execjs
from urllib import parse


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

    def get_tk(self, text):
        return self.ctx.call("TL", text)


class Translate(object):
    def __init__(self, to_language='zh-TW', this_language='en', read=False):
        self.this_language = this_language
        self.to_language = to_language
        self.read = read
        self.js = Py4Js()

    def open_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = requests.get(url=url, headers=headers, timeout=8)

        return req

    def build_url(self, text, tk):
        baseUrl = 'http://translate.google.cn/translate_a/single'
        baseUrl += '?client=webapp&'
        baseUrl += 'sl=%s&' % self.this_language
        baseUrl += 'tl=%s&' % self.to_language
        baseUrl += 'hl=zh-CN&'
        baseUrl += 'dt=at&'
        baseUrl += 'dt=bd&'
        baseUrl += 'dt=ex&'
        baseUrl += 'dt=ld&'
        baseUrl += 'dt=md&'
        baseUrl += 'dt=qca&'
        baseUrl += 'dt=rw&'
        baseUrl += 'dt=rm&'
        baseUrl += 'dt=ss&'
        baseUrl += 'dt=t&'
        baseUrl += 'ie=UTF-8&'
        baseUrl += 'oe=UTF-8&'
        baseUrl += 'clearbtn=1&'
        baseUrl += 'otf=1&'
        baseUrl += 'pc=1&'
        baseUrl += 'srcrom=0&'
        baseUrl += 'ssel=0&'
        baseUrl += 'tsel=0&'
        baseUrl += 'kc=2&'
        baseUrl += 'tk=' + str(tk) + '&'
        baseUrl += 'q=' + parse.quote(text)
        return baseUrl

    def translate(self, text):

        tk = self.js.get_tk(text)

        if len(text) > 4891:
            raise Exception("超過翻譯長度限制")
        url = self.build_url(text, tk)
        _result = self.open_url(url)
        data = _result.content.decode('utf-8')

        tmp = json.loads(data)
        json_array = tmp[0]
        result = None
        for json_item in json_array:
            if json_item[0]:
                if result:
                    result = result + " " + json_item[0]
                else:
                    result = json_item[0]
        return result


if __name__ == '__main__':
    t = """According to Musk, you can’t learn what you can’t connect. After all, many memory experts note that the best way to remember something is to associate it with something you already know. If there are no mental "hooks" for new knowledge to catch on, it tends to go in one ear and out the other."""
    ts = Translate('zh-TW', 'en')
    result = ts.translate(t)
    print(result)
