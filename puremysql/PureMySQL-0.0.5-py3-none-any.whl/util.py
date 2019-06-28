# -*- coding: utf-8 -*-

# @Date    : 2019-06-28
# @Author  : Peng Shiyu

from six.moves.urllib_parse import urlparse
import re


def parse_db_url(url):
    """
    解析bd_url
    :param url: str
    :return: dict
    """
    parse_result = urlparse(url)
    result = re.match("(?P<user>.*):(?P<password>.*)@(?P<host>.*):(?P<port>\d+)", parse_result.netloc)
    groupdict = result.groupdict()

    db_config = {
        "scheme": parse_result.scheme,
        "database": parse_result.path.strip("/"),

        "user": groupdict.get("user"),
        "password": groupdict.get("password"),
        "host": groupdict.get("host"),
        "port": groupdict.get("port")
    }

    for query in parse_result.query.split("&"):
        key_value = query.split("=")
        if len(key_value) == 2:
            key, value = key_value
            db_config[key] = value

    return db_config


if __name__ == '__main__':
    url = "mysql://root:123456@127.0.0.1:3306/demo?charset=utf8"

    print(parse_db_url(url))
    # {
    #     'scheme': 'mysql',
    #     'database': 'demo',
    #     'user': 'root',
    #     'password': '123456',
    #     'host': '127.0.0.1',
    #     'port': '3306',
    #     'charset': 'utf8'
    # }
