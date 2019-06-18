from django.core.management.base import BaseCommand
from autopost.utils.crawler import QtCrawler


class Command(BaseCommand):
    help = '执行文章自动抓取'

    def add_arguments(self, parser):
        parser.add_argument('auto_id', type=str)

    def handle(self, *args, **options):
        task_id = int(options['auto_id'])
        print('获取远程文章抓取, 任务ID:%d' % task_id)
        crawler = QtCrawler()
        try:
            result = crawler.crawl_news(task_id=task_id)
            if result:
                message = '任务执行成功,请在文章列表查看.'
            else:
                message = '任务执行失败,请检查系统LOG.'
        except Exception as e:
            message = '任务执行失败,原因:%s' % str(e)
        print(message)
