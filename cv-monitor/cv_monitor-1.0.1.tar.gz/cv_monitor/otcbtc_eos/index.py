from bs4 import BeautifulSoup
import requests
import json
import pymysql
import conf

config = conf.config

buy_max = 0
buy_min = 0
sell_max = 0
sell_min = 0


def notice(send_message, is_at):
    at = []
    if is_at:
        at = config['ding_notice_at']
    params = {
        "msgtype": "text",
        "text": {
            "content": send_message
        },
        "at": {
            "atMobiles": at,
            "isAtAll": False
        }
    }

    headers = {'Content-Type': 'application/json'}

    requests.post(url=config['ding_notice_url'], headers=headers, data=json.dumps(params))


# 可选项，是否插入到数据库中
def insert_mysql():
    db = pymysql.connect("127.0.0.1", "root", "root", "eos_info")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 插入语句
    sql = "INSERT INTO `eos_info`.`otcbtc_price`( `buy_max`, `buy_min`, `sell_max`, `sell_min`) " \
          "VALUES ( " + buy_max + ", " + buy_min + ", " + sell_max + ", " + sell_min + ")"
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 如果发生错误则回滚
        db.rollback()

    # 关闭数据库连接
    db.close()


def main():
    # 购买 EOS 单价
    html_doc = requests.get(config['otc_buy_url']).content.decode()

    # 使用 html.parser 解析器
    soup = BeautifulSoup(html_doc, 'html.parser')

    # 获取页面里所有标签为 p 的，并生成列表
    main_tag = soup.find_all("p")

    # 单价对应的类,recent-average-price
    info = soup.select("li.price")

    buy_price = []

    for item in info:
        message = [text for text in item.stripped_strings]
        buy_price.insert(0, message[1])

    # 售卖 EOS 单价
    html_doc = requests.get(config['otc_sell_url']).content.decode()

    # 使用 html.parser 解析器
    soup = BeautifulSoup(html_doc, 'html.parser')

    # 获取页面里所有标签为 p 的，并生成列表
    main_tag = soup.find_all("p")

    # 获取OTC推荐的卖家列表
    info = soup.select("li.price")

    sell_price = []

    for item in info:
        message = [text for text in item.stripped_strings]
        sell_price.insert(0, message[1])

    buy_max = max(buy_price)
    buy_min = min(buy_price)

    sell_max = max(sell_price)
    sell_min = min(sell_price)

    message = "----------------------\n" \
              "OTC_BTC 实时价格" \
              "\n----------------------\n\n" \
              "购买 EOS：" \
              "\n\t最高价格：{0};" \
              "\n\t最低价格：{1};\n\n" \
              "出售 EOS：\n\t最高价格：{2};" \
              "\n\t最低价格：{3};" \
              "\n\n----------------------\n" \
              "通知阀值：" \
              "\n\t卖出最大值：{4};" \
              "\n\t买入最小值：{5}; " \
              "\n----------------------"
    result = message.format(buy_max, buy_min, sell_max, sell_min, config['max'], config['min'])

    print(buy_price, sell_price, result)

    if float(buy_min) <= config['min'] or float(sell_max) >= config['max']:
        notice(result, True)
    else:
        notice(result, False)


main()
