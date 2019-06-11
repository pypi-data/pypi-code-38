import logging

logger = logging.getLogger('humanSpider')
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(name)s:%(levelname)s: %(message)s")
console.setFormatter(formatter)

logger.addHandler(console)


# 爬虫相关默认配置
DOMAIN = None
USER_AGENT = 'humanSpider'  # 默认UA
DEFAULT_COOKIES = None  # cookie
SLEEP_TIME = 0.05  # 间隔时间
RETRY_NUM = 3  # 重试次数
RETRY_SLEEP_TIME = 1  # 重试间隔
TIMEOUT = 180  # 超时时间
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}  # 默认请求头

