# -*- coding: utf-8 -*-
# Created by crazyX on 2018/7/13
from socket import timeout
from http import cookiejar
from bs4 import BeautifulSoup
from urllib import request, parse
from urllib.error import URLError, HTTPError

from ojcrawler.crawlers.base import OJ
from ojcrawler.crawlers.config import logger, save_image
from ojcrawler.crawlers.config import HTTP_METHOD_TIMEOUT


class HDU(OJ):
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
        return 'http://acm.hdu.edu.cn/'

    def url_problem(self, pid):
        return self.url_home + 'showproblem.php?pid={}'.format(pid)

    @property
    def url_login(self):
        return self.url_home + 'userloginex.php?action=login'

    @property
    def url_submit(self):
        return self.url_home + 'submit.php?action=submit'

    @property
    def url_status(self):
        return self.url_home + 'status.php?'

    @property
    def http_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Ubuntu Chromium/52.0.2743.116 Chrome/52.0.2743.116 Safari/537.36',
            'Origin': "http://acm.hdu.edu.cn",
            'Host': "acm.hdu.edu.cn",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
        }

    @property
    def uncertain_result_status(self):
        # lower
        return ['queuing', 'compiling', 'running']

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
        # hdu支持语言不太可能发生变化
        return {
            'G++': '0',
            'GCC': '1',
            'C++': '2',
            'C': '3',
            'PASCAL': '4',
            'JAVA': '5',
            'C#': '6',
        }

    def login(self):
        data = dict(
            username=self.handle,
            userpass=self.password,
            login='Sign In'
        )
        ret = self.post(self.url_login, data)
        if ret:
            html = ret.read().decode('gbk')
            if html.find('signout') > 0:
                return True, ''
            else:
                return False, '账号密码不匹配'
        else:
            return False, '登陆：http方法错误，请检查网络后重试'

    def is_login(self):
        ret = self.get(self.url_home)
        if ret:
            html = ret.read().decode('gbk')
            return True if html.find('<img alt="Author"') > 0 else False
        else:
            return False

    def replace_image(self, html):
        # http://acm.hdu.edu.cn/showproblem.php?pid=3987
        # http://acm.hdu.edu.cn/showproblem.php?pid=1033
        pos = html.find('<img')
        if pos == -1:
            return html
        src_pos = html[pos:].find('src=')
        stp = pos + src_pos + 5
        edp = html[stp + 1:].find('"') + stp
        url = html[stp: edp + 1]
        image_url = self.url_home + url[url.find('/data/') + 1:]
        saved_url = self.image_func(image_url, self.oj_name)

        return html[:stp] + saved_url + self.replace_image(html[edp + 1:])

    def get_problem(self, pid):
        ret = self.get(self.url_problem(pid))
        if ret:
            html = ret.read()
            # 不需要decode，交给BeautifulSoup处理
            soup = BeautifulSoup(html, 'html5lib')
            msg_png = soup.find('img', {'src': '/images/msg.png'})
            if msg_png:
                return False, soup.find('td', {'valign': 'middle'}).find('div').text
            else:
                title = soup.find('h1', {'style': 'color:#1A5CC8'}).text

                spj = soup.find('font', {'color': 'red'})
                problem_type = 'special judge' if (spj and 'Special Judge' == spj.text) else 'regular'

                origin = self.url_problem(pid)

                limits = soup.find('span', {'style': 'font-family:Arial;font-size:12px;font-weight:bold;color:green'})
                limits_list = limits.contents[0].split(' ')
                time_java, time_default = [int(x) for x in limits_list[2].split('/')]
                memory_java, memory_default = [int(x) for x in limits_list[6].split('/')]
                ac_submit = limits.contents[2].replace('\xa0', ' ').split(' ')

                limits = {
                    'default': (time_default, memory_default),
                    'java': (time_java, memory_java),
                }

                samples_input = []
                samples_output = []
                samples = {}

                descriptions = []
                category = ''
                tags = []
                append_html = ''

                # 题面
                panel_titles = soup.find_all('div', {'class': 'panel_title'})
                panel_contents = soup.find_all('div', {'class': 'panel_content'})
                assert len(panel_titles) == len(panel_contents)
                n = len(panel_titles)
                for i in range(n):
                    if panel_titles[i].text == 'Sample Input':
                        samples_input.append(panel_contents[i].text)
                    elif panel_titles[i].text == 'Sample Output':
                        samples_output.append(panel_contents[i].text)
                    elif panel_titles[i].text == 'Source':
                        category = panel_contents[i].text
                    else:
                        descriptions.append(
                            (panel_titles[i].text,
                             self.replace_image(str(panel_contents[i]))
                             )
                        )
                assert len(samples_input) == len(samples_output) or len(samples_input) == 0
                n = len(samples_output)
                if len(samples_input) != 0:
                    for i in range(n):
                        samples[i + 1] = (samples_input[i], samples_output[i])
                else:
                    for i in range(n):
                        samples[i + 1] = ("", samples_output[i])

                compatible_data = {}
                for key in self.compatible_problem_fields:
                    compatible_data[key] = eval(key)

                # 增加题目提交数和ac数
                try:
                    compatible_data['accepted_number'] = int(ac_submit[-1])
                    compatible_data['submitted_number'] = int(ac_submit[2])
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
            problemid=pid,
            language=self.get_languages()[lang.upper()],
            usercode=source,
            check='0',
        )
        ret = self.post(self.url_submit, data)
        if ret:
            # 不直接用重定向页面是因为，并发高的时候，第一个提交并不一定是自己的
            if ret.url == self.url_status[:-1]:
                ok, info = self.get_result()
                return (True, info['rid']) if ok else (False, '提交代码（获取提交id）：' + info)
            elif ret.url == self.url_submit:
                html = ret.read()
                soup = BeautifulSoup(html, 'html5lib')
                return False, soup.find('div', {'style': 'color:red; font-size:12px'}).text
            else:
                return False, '提交代码：未知错误'
        else:
            return False, '提交代码：http方法错误，请检查网络后重试'

    def _get_result(self, url_result):
        # 获取url_result下的第一个结果
        ret = self.get(url_result)
        if ret:
            html = ret.read()
            soup = BeautifulSoup(html, 'html5lib')
            table = soup.find('table', {'class': 'table_text'})
            trs = table.find_all('tr')
            if len(trs) <= 1:
                return False, '没有结果'
            else:
                # 第一行为header
                data = {
                    'rid': trs[1].contents[0].text.strip(),
                    'status': trs[1].contents[2].text.strip(),
                    'time': int(trs[1].contents[4].text.strip()[:-2]),
                    'memory': int(trs[1].contents[5].text.strip()[:-1]),
                    'ce_info': '',
                }
                if data['status'] == 'Compilation Error':
                    ret, info = self.get_compile_error_info(data['rid'])
                    data['ce_info'] = info if ret else ''
                return True, data
        else:
            return False, '获取结果：http方法错误，请检查网络后重试'

    def get_result(self):
        # 只需要获取自己最近一次提交的结果
        return self.get_result_by_user(self.handle)

    def get_result_by_user(self, handle):
        url = self.url_status + 'user={}'.format(handle)
        return self._get_result(url)

    def get_result_by_rid(self, rid):
        url = self.url_status + 'first={}'.format(rid)
        return self._get_result(url)

    def get_compile_error_info(self, rid):
        url = self.url_home + 'viewerror.php?rid={}'.format(rid)
        ret = self.get(url)
        if ret:
            html = ret.read()
            soup = BeautifulSoup(html, 'html5lib')
            title = soup.find('h1')
            if title.text == 'View Compilation Error':
                return True, soup.find('pre').text
            else:
                return False, soup.find('td', {'valign': 'middle'}).text
        else:
            return False, '获取编译错误信息：http方法错误，请检查网络后重试'
