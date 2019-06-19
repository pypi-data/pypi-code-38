#!/usr/bin/env python3

from oslo_config import cfg
import requests
import time

CONF = cfg.CONF

cli_opts = [
    cfg.IntOpt('number',
               short='n',
               default=0,
               help='餐券数目'),
    cfg.StrOpt('work_type',
               short='t',
               choices=[
                   ('工作日加班', '工作日加班'),
                   ('节假日加班', '节假日加班'),
                   ('周末加班', '周末加班'),
               ],
               default='工作日加班',
               help='加班类型'),
    cfg.StrOpt('reason',
               short='r',
               default='请填写加班原因',
               help='加班原因'),
    cfg.StrOpt('caipu',
               short='c',
               choices=[
                   ('春光餐券', '春光餐券'),
                   ('亚新餐券', '亚新餐券'),
               ],
               default='春光餐券',
               help='餐券类型'),
    cfg.BoolOpt('doorder',
               short='d',
               help='是否订餐'),

]
common_opts = [
    cfg.StrOpt('name',
               default='胡月恒',
               help='订餐人'),
    cfg.StrOpt('email_prefix',
               default='huyueheng',
               help='邮箱'),
    cfg.StrOpt('bind_host',
               default='10.180.201.253',
               help='host'),
    cfg.IntOpt('bind_port',
               default=8080,
               help='port'),
]



def food(conf):
    def _make_url(bind_host=conf.bind_host, bind_port=conf.bind_port, nag='order.do', timestamp=int(time.time() * 1000)):
        return f'http://{bind_host}:{bind_port}/food/{nag}?timestamp={timestamp}'
    url = _make_url()
    if not conf.doorder:
        url = _make_url(nag='orderlist.do')
        text = requests.get(url=url).text
        print(text)
        return text

    headers = {'Host': '10.180.201.253:8080',
               'Connection': 'keep-alive',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Origin': 'http://10.180.201.253:8080',
               'X-Requested-With': 'XMLHttpRequest',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
               'DNT': '1',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Referer': 'http://10.180.201.253:8080/food/',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
               'Cookie': 'JSESSIONID=98D14289347B4A3B6D72D6D3B4F93A81'}

    work_date = time.strftime('%Y-%m-%d', time.localtime())

    data_str = f'''
        'userName': '{conf.name}',
        'bumen': '系统软件部研发五处',
        'caipu': '{conf.caipu}',
        'workType': '{conf.work_type}',
        'reason': '{conf.reason}',
        'workDate': '{work_date}',
        'num': '{conf.number}',
        'email': '{conf.email_prefix}'
        '''
    data = eval("{" + data_str + "}")
    print(requests.post(url=url, data=data, headers=headers).text)


def main():
    # 注册命令行参数
    CONF.register_cli_opts(cli_opts)
    # 注册配置
    CONF.register_opts(common_opts)
    # 解析参数
    CONF(default_config_files=['~/.toutetu/food.conf'])
    food(CONF)


if __name__ == '__main__':
    main()
