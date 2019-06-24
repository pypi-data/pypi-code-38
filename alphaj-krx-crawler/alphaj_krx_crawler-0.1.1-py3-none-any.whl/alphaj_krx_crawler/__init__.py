import requests
import csv
import calendar
import datetime
from datetime import timedelta


holidays = ["20190301", "20190501", "20190506", "20190606", "20190815",
            "20190912", "20191003", "20191009", "20191225", "20191231"]


def check_day_is_holiday(day):
    if day in holidays:
        return True
    else:
        return False


def check_day_is_weekend(date):
    weekday = calendar.weekday(date.year, date.month, date.day)

    if weekday in [5, 6]:
        return True
    else:
        return False

def save_stock_list_as_excel(file_name, target_date=None):
    otp_url = "http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx"
    s = requests.Session()

    if target_date is not None:
        today = target_date
    else:
        today = datetime.datetime.today()

    while True:
        if check_day_is_weekend(today):
            today = today - timedelta(days=1)
            continue
        if check_day_is_holiday(today):
            today = today - timedelta(days=1)
            continue
        break

    otp_data = {
        "name": "fileDown",
        "filetype": "csv",
        "url": "MKD/03/0303/03030103/mkd03030103",
        "tp_cd": "ALL",
        "date": today.strftime('%Y%m%d'),
        "lang": "ko",
        "pagePath": "/contents/MKD/03/0303/03030103/MKD03030103.jsp"

    }

    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }

    otp_res = s.get(otp_url, params=otp_data, headers=header)

    down_url = "http://file.krx.co.kr/download.jspx"

    down_params = {"code": otp_res.text}

    req_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Referer": otp_url
    }

    down_res = s.post(down_url, data=down_params, headers=req_header)

    # decoded_content = down_res.content.decode('utf-8')

    with open("{}.csv".format(file_name), "wb") as csv_file:
        csv_file.write(down_res.content)
        


def get_stock_list_from_krx(target_date=None):
    otp_url = "http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx"
    s = requests.Session()

    if target_date is not None:
        today = target_date
    else:
        today = datetime.datetime.today()

    while True:
        if check_day_is_weekend(today):
            today = today - timedelta(days=1)
            continue
        if check_day_is_holiday(today):
            today = today - timedelta(days=1)
            continue
        break

    otp_data = {
        "name": "fileDown",
        "filetype": "csv",
        "url": "MKD/03/0303/03030103/mkd03030103",
        "tp_cd": "ALL",
        "date": today.strftime('%Y%m%d'),
        "lang": "ko",
        "pagePath": "/contents/MKD/03/0303/03030103/MKD03030103.jsp"

    }

    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }

    otp_res = s.get(otp_url, params=otp_data, headers=header)

    down_url = "http://file.krx.co.kr/download.jspx"

    down_params = {"code": otp_res.text}

    req_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Referer": otp_url
    }

    down_res = s.post(down_url, data=down_params, headers=req_header)

    decoded_content = down_res.content.decode('utf-8')


    cr = csv.reader(decoded_content.splitlines(), delimiter=',')

    my_list = list(cr)

    result = []

    for row in my_list:
        result.append({
            'market': row[0],
            'stock_code': row[1],
            'stock_name': row[2],
            'category': row[3],
            'market_capital': row[-1]
        })

    return result
