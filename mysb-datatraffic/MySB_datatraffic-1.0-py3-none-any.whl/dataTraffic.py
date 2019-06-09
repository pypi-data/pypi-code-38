import re
import sqlite3
import requests
import datetime
from bs4 import BeautifulSoup

class dataTraffic:

    def __init__(self, telnum, password, line_access_token):
        self.telnum = telnum
        self.password = password
        self.line_access_token = line_access_token

    def login(self):
        session = requests.Session()
        req = session.get('https://my.softbank.jp/msb/d/webLink/doSend/MSB020063')
        soup = BeautifulSoup(req.text, 'lxml')
        ticket = soup.find('input', type='hidden').get('value')
        payload = {
            'telnum': self.telnum,
            'password': self.password,
            'ticket': ticket
        }
        session.post('https://id.my.softbank.jp/sbid_auth/type1/2.0/login.php', data=payload)
        return session

    def get_data(self):
        session = self.login()
        req = session.get('https://my.softbank.jp/msb/d/webLink/doSend/MRERE0000')
        soup = BeautifulSoup(req.text, 'lxml')
        auth_token = soup.find_all('input')
        payload = {
            'mfiv': auth_token[0].get('value'),
            'mfsb': auth_token[1].get('value'),
        }
        res = session.post('https://re11.my.softbank.jp/resfe/top/', data=payload)
        m = re.findall('<span>(.+?)</span>GB', res.text)
        remain = float(m[2])
        total = float(m[1])
        used = float(m[0])
        rate = round(remain / total * 100, 1)
        return remain, total, used, rate

    def line(self, message):
        line_notify_token = self.line_access_token
        line_notify_api = 'https://notify-api.line.me/api/notify'
        payload = {'message': message}
        headers = {'Authorization': 'Bearer ' + line_notify_token}
        line_notify = requests.post(line_notify_api, data=payload, headers=headers)
    
    def send_data(self):
        data = self.get_data()
        text = '\n{}GB / {}GB ({}%)'.format(data[0], data[1], data[3])
        self.line(message=text)

    #修正中
    def add_database(self, remain=None, total=None, used=None, rate=None):
        time = datetime.date.today()
        tablename = time.strftime('data_%Y_%m')
        timedata = time.strftime('%Y_%m_%d')
        conn = sqlite3.connect('trafficData.db')
        c = conn.cursor()
        if time.day == 1:
            order = 'create table {}(time, remain real, total real, used real , rate real);'.format(tablename)
            c.execute(order)
        order = 'insert into {} values("{}", {}, {}, {}, {});'.format(tablename, timedata, remain, total, used, rate)
        c.execute(order)
        conn.commit()
        conn.close()
