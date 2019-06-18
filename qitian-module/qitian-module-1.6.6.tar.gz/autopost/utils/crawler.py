from autopost.models import AutoTask, CrawlLogs
from urllib import request
from bs4 import BeautifulSoup
import json
from autopost.utils.html import HtmlStorage
from autopost.models import Article, Category


class QtCrawler:
    """
    简易爬虫代码
    """

    task = None

    def crawl_news(self, task_id):
        try:
            self.task = AutoTask.objects.get(pk=task_id)
        except AutoTask.DoesNotExist:
            return False
        # 根据规则找出文章列表
        self.crawl_list(self.task.url, self.task.list_selector)
        return True

    @staticmethod
    def get_content(url):
        """
        封装url请求
        :param url:
        :return: Beautifulsoup content
        """
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = request.Request(url, headers=headers)
        resp = request.urlopen(req)
        bs_content = BeautifulSoup(resp, 'lxml')
        return bs_content, req

    def crawl_list(self, url, pattern, preview=False):
        html, req = self.get_content(url)
        articles = html.select(pattern)

        ret_data = list()
        for article in articles:
            if 'href' not in article.attrs:
                continue
            item_url = article['href']
            item_title = article.string

            # 完善URL
            url_base = req.full_url.replace(req.selector, '')
            if str(item_url).startswith('//'):
                item_url = req.type + ':' + item_url
            if not str(item_url).startswith('http') and not str(item_url).startswith('//'):
                item_url = url_base + item_url
            if not preview:
                # 抓取文章详情
                try:
                    title, html_content, first_img, key_words, summery = self.crawl_detail(item_url,
                                                                                           self.task.title_selector,
                                                                                           self.task.content_selector,
                                                                                           self.task.content_except,
                                                                                           self.task.title_replace,
                                                                                           self.task.content_replace,
                                                                                           lazy_photo=self.task.lazy_photo,
                                                                                           )
                    if not Article.objects.filter(title=title).exists():
                        self.save_article(title, html_content, first_img, key_words, summery)

                except ChildProcessError:
                    continue
            ret_data.append({'title': item_title, 'url': item_url})
        return ret_data

    def crawl_detail(self, url, title_pattern, content_pattern, content_exclude, title_replace, content_replace,
                     lazy_photo='', fetch_img=True,
                     preview=False):
        """
        抓取文章详情
        :param url:
        :param title_pattern:
        :param content_pattern:
        :param content_exclude:
        :param title_replace:
        :param content_replace:
        :param lazy_photo:
        :param fetch_img:
        :param preview:
        :return:
        """
        html, req = self.get_content(url)
        try:
            title = html.select_one(title_pattern).text.strip()
            # 检查文章是否被抓取过 不同站点可以重复抓取
            if not preview and CrawlLogs.objects.filter(title=title, site=self.task.site).exists():
                # 直接返回文章
                db_article = Article.objects.filter(title=title).get()
                return db_article.title, db_article.content, db_article.thumbnail, db_article.keywords, db_article.summery
            main_content = html.select_one(content_pattern)
        except Exception:
            raise ChildProcessError
        try:
            exclude_obj = json.loads(content_exclude)
            if 'script' not in exclude_obj:
                exclude_obj.append('script')
        except Exception:
            exclude_obj = ['script']
        for item in exclude_obj:
            try:
                main_content.select_one(item).replace_with('')
            except Exception:
                continue
        try:
            title_rule = eval(title_replace)
            for item in title_rule:
                title = str(title).replace(item[0], item[1])
        except:
            print('Do not need replace title.')

        # 获取图片上传
        html_content, first_img, key_words, summery = HtmlStorage.save_content(main_content, send_qiniu=True,
                                                                               save_img=fetch_img,
                                                                               lazy_photo=lazy_photo)
        try:
            content_rule = eval(content_replace)
            for item in content_rule:
                html_content = html_content.replace(item[0], item[1])
        except Exception as e:
            print('Do not need replace content. %s' % str(e))
        if preview:
            return title, html_content
        else:
            url_base = req.full_url.replace(req.selector, '')
            crawl_log = CrawlLogs()
            crawl_log.title = title
            crawl_log.url = url
            crawl_log.site = self.task.site
            crawl_log.site_url = url_base
            crawl_log.save()
        return title, html_content, first_img, key_words, summery

    def save_article(self, title, html_content, first_img, key_words, summery):
        """
        保存文章
        :param title:
        :param html_content:
        :param first_img:
        :param key_words:
        :param summery:
        :return:
        """
        article = Article()
        article.site = self.task.site
        article.category = self.task.category
        article.title = title
        article.content = html_content
        article.keywords = key_words
        article.summery = summery
        article.thumbnail = first_img
        article.author = self.task.author
        article.save()
        return article
