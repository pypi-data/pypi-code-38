# -*- coding: utf-8 -*-
# Created by crazyX on 2018/7/8
from socket import timeout
from http import cookiejar
from bs4 import BeautifulSoup
from urllib import request, parse
from urllib.error import URLError, HTTPError

from ojcrawler.crawlers.base import OJ
from ojcrawler.crawlers.config import logger, save_image
from ojcrawler.crawlers.config import HTTP_METHOD_TIMEOUT


class POJ(OJ):
    def __init__(self, handle, password, image_func=save_image):
        super().__init__(handle, password, image_func)

        # 声明一个CookieJar对象实例来保存cookie
        cookie = cookiejar.CookieJar()
        # 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
        handler = request.HTTPCookieProcessor(cookie)
        # 通过handler来构建opener
        self.opener = request.build_opener(handler)
        # 此处的open方法同urllib2的urlopen方法，也可以传入request

    @property
    def browser(self):
        return self.opener

    @property
    def url_home(self):
        return 'http://poj.org/'

    def url_problem(self, pid):
        return self.url_home + 'problem?id={}'.format(pid)

    @property
    def url_login(self):
        return self.url_home + 'login?'

    @property
    def url_submit(self):
        return self.url_home + 'submit?'

    @property
    def url_status(self):
        return self.url_home + 'status?'

    @property
    def http_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Ubuntu Chromium/52.0.2743.116 Chrome/52.0.2743.116 Safari/537.36',
            'Origin': "http://poj.org",
            'Host': "poj.org",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
        }

    @property
    def uncertain_result_status(self):
        # lower
        return ['running & judging', 'compiling', 'waiting']

    def post(self, url, data):
        post_data = parse.urlencode(data).encode()
        req = request.Request(url, post_data, self.http_headers)
        try:
            return self.opener.open(req, timeout=HTTP_METHOD_TIMEOUT)
        except (HTTPError, URLError) as error:
            logger.error('Data not retrieved because %s\nURL: %s', error, url)
        except timeout:
            logger.error('socket timed out\nURL: %s', url)

    @staticmethod
    def get_languages():
        # poj支持语言不太可能发生变化
        return {
            'G++': '0',
            'GCC': '1',
            'JAVA': '2',
            'PASCAL': '3',
            'C++': '4',
            'C': '5',
            'FORTRAN': '6',
        }

    def login(self):
        data = dict(
            user_id1=self.handle,
            password1=self.password,
            B1='login',
            url='.',
        )
        ret = self.post(self.url_login, data)
        if ret:
            html = ret.read().decode()
            if html.find('loginlog') > 0:
                return True, ''
            else:
                return False, '账号密码不匹配'
        else:
            return False, '登陆：http方法错误，请检查网络后重试'

    def is_login(self):
        ret = self.get(self.url_home)
        if ret:
            html = ret.read().decode()
            return True if html.find('loginlog') > 0 else False
        else:
            return False

    def replace_image(self, html):
        pos = html.find('<img src=')
        if pos == -1:
            return html
        end_pos = html[pos:].find('>')
        left = pos + 10
        right = pos + end_pos - 2
        image_url = self.url_home + html[left:right]
        saved_url = self.image_func(image_url, self.oj_name)
        return html[:left] + saved_url + self.replace_image(html[right:])

    def get_problem(self, pid):
        ret = self.get(self.url_problem(pid))
        if ret:
            html = ret.read().decode()
            soup = BeautifulSoup(html, 'html5lib')
            title = soup.find('title').text
            if title == 'Error':
                return False, soup.find('li').text
            else:
                title = soup.find('div', {'class': 'ptt'}).text
                plm = soup.find('div', {'class': 'plm'})
                limits = plm.find_all('td')
                problem_type = 'special judge' if 'Special Judge' in [x.text for x in limits] else 'regular'
                origin = self.url_problem(pid)
                ac_submit = [limits[5].text, limits[3].text, ]
                limits = {
                    'default': (int(limits[0].contents[1].strip()[:-2]),
                                int(limits[2].contents[1].strip()[:-1])),
                    'java': (3 * int(limits[0].contents[1].strip()[:-2]),
                             int(limits[2].contents[1].strip()[:-1])),
                }

                samples_input = []
                samples_output = []
                samples = {}

                descriptions = []
                category = ''
                tags = []
                append_html = ''

                items = plm.find_next_siblings()
                n = len(items)
                assert n % 2 == 0
                for i in range(0, n, 2):
                    sub_title = items[i].text.strip()
                    sub_content = items[i + 1]
                    if sub_title == 'Sample Input':
                        samples_input.append(sub_content.text)
                    elif sub_title == 'Sample Output':
                        samples_output.append(sub_content.text)
                    elif sub_title == 'Source':
                        category = sub_content.text
                    else:
                        descriptions.append(
                            (sub_title,
                             self.replace_image(str(sub_content))
                             )
                        )

                assert len(samples_input) == len(samples_output)
                n = len(samples_input)
                for i in range(n):
                    samples[i + 1] = (samples_input[i], samples_output[i])

                compatible_data = {}
                for key in self.compatible_problem_fields:
                    compatible_data[key] = eval(key)

                # 增加题目提交数和ac数
                try:
                    compatible_data['accepted_number'] = int(ac_submit[0].split(':')[1])
                    compatible_data['submitted_number'] = int(ac_submit[1].split(':')[1])
                except Exception as e:
                    logger.warning("获取submit和ac数失败({})：".format(pid) + str(e))

                return True, compatible_data
        else:
            return False, '获取题目：http方法错误，请检查网络后重试'

    def submit_code(self, source, lang, pid):
        if not self.is_login():
            success, info = self.login()
            if not success:
                return False, info
        data = dict(
            problem_id=pid,
            language=self.get_languages()[lang.upper()],
            source=source,
            submit='Submit',
            encoded='0',
        )
        ret = self.post(self.url_submit, data)
        if ret:
            # 不直接用重定向页面是因为，并发高的时候，第一个提交并不一定是自己的
            if ret.url == self.url_status[:-1]:
                ok, info = self.get_result()
                return (True, info['rid']) if ok else (False, '提交代码（获取提交id）：' + info)
            else:
                html = ret.read().decode()
                soup = BeautifulSoup(html, 'html5lib')
                err = soup.find('font', {'size': 4})
                if err and err.text == 'Error Occurred':
                    return False, soup.find('li').text
                else:
                    return False, '提交代码：未知错误'
        else:
            return False, '提交代码：http方法错误，请检查网络后重试'

    def _get_result(self, url_result):
        # 获取url_result下的第一个结果
        ret = self.get(url_result)
        if ret:
            html = ret.read().decode()
            soup = BeautifulSoup(html, 'html5lib')
            table = soup.find('table', {'class': 'a'})
            trs = table.find_all('tr')
            if len(trs) <= 1:
                return False, '没有结果'
            else:
                # 第一行为header
                # 因为获取结果的时候是肯定知道rid的，rid对应到一个具体的提交，所以只需要提交的结果信息
                data = {
                    'rid':  trs[1].contents[0].text.strip(),
                    'status': trs[1].contents[3].text.strip(),
                    'memory': trs[1].contents[4].text.strip(),
                    'time': trs[1].contents[5].text.strip(),
                    'ce_info': '',
                }
                if data['status'] == 'Compile Error':
                    ret, info = self.get_compile_error_info(data['rid'])
                    data['ce_info'] = info if ret else ''
                return True, data
        else:
            return False, '获取结果：http方法错误，请检查网络后重试'

    def get_result(self):
        # 只需要获取自己最近一次提交的结果
        return self.get_result_by_user(self.handle)

    def get_result_by_user(self, handle):
        url = self.url_status + 'user_id={}'.format(handle)
        return self._get_result(url)

    def get_result_by_rid(self, rid):
        rid = int(rid)
        url = self.url_status + 'top={}'.format(rid + 1)
        return self._get_result(url)

    def get_compile_error_info(self, rid):
        url = self.url_home + 'showcompileinfo?solution_id={}'.format(rid)
        ret = self.get(url)
        if ret:
            html = ret.read().decode()
            soup = BeautifulSoup(html, 'html5lib')
            pre = soup.find('pre')
            if pre:
                return True, pre.text
            else:
                return True, None
        else:
            return False, '获取编译错误信息：http方法错误，请检查网络后重试'
