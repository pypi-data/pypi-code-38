from .base import BaseBuilder

import datetime
import math
import os

class BlogBuilder(BaseBuilder):

    def __init__(self, site):
        super().__init__(site)
        self.blog_pages_by_language = {}

    def index(self, params, language):
        articles = self.parse_articles(params.get('articles', []), language)
        blog_pages = self.paginate_articles(self.sort_articles(articles))
        self.blog_pages_by_language[language] = blog_pages
        links = self.create_links(blog_pages, articles, language)
        return {
            'links' : links,
            'vars' : {
                'articles' : articles
            },
        }

    def get_index_slug(self, language, i):
        return os.path.join(
            self.get_blog_prefix(language),
            'index{}'.format('-{}'.format(i) if i != 0 else '')
        )

    def create_links(self, blog_pages, articles, language):
        links = {}
        for i, blog_page in enumerate(blog_pages):
            slug = self.get_index_slug(language, i)
            link = self.site.get_link_dst(slug, language)
            links['blog-{}'.format(i)] = link
            if i == 0:
                links['blog'] = link

            for article in articles:
                links['blog-{}'.format(article['name'])] = article['dst']
        return links

    def build(self):
        for language, blog_pages in self.blog_pages_by_language.items():
            self.build_blog(blog_pages, language)

    def sort_articles(self, articles):
        sorted_articles = list(reversed(sorted(articles, key=lambda x : x.get('date',x.get('title')))))
        return sorted_articles

    def paginate_articles(self, articles):
        app = self.site.config.get('articles-per-page', 10)
        return [articles[i*app:(i+1)*app] for i in range(math.ceil(len(articles)/app))]

    def build_blog(self, blog_pages, language):
        """
        Build the indexes, meta-pages and articles.
        """
        for i, blog_page in enumerate(blog_pages):
            self.build_index_site(i, len(blog_pages), blog_page, language)
            for article in blog_page:
                self.build_article(article, i, language)

    def get_blog_prefix(self, language):
        return self.site.config['languages'][language].get('blog-path', 'blog')

    def build_index_site(self, i, n, blog_page, language):
        input = "{% extends('index.html') %}"
        vars = {
            'blog_page' : blog_page,
            'i' : i,
            'n' : n,
        }
        slug = self.get_index_slug(language, i)
        dst = self.site.get_dst(slug, language)
        output = self.site.process(input, {'type' : 'html'}, vars, language)
        self.site.write(output, dst)

    def build_article(self, article, page, language):
        """
        Build an individual blog article.
        """
        vars = {
            'article' : article,
            'blog_page' : page,
            'index_link' : self.site.get_link(language, 'blog-{}'.format(page)),
        }
        input = self.site.load(article['src'])
        output = self.site.process(input, article, vars, language)
        self.site.write(output, article['dst'])

    def parse_articles(self, articles, language):
        parsed_articles = self.site.parse_objs(articles, language, prefix=self.get_blog_prefix(language))
        for article in parsed_articles:
            date_format = self.site.config['languages'][language].get('date-format', '%Y-%m-%d')
            article['date'] = datetime.datetime.strptime(article['date'], '%Y-%m-%d %H:%M')
            article['date-str'] = article['date'].strftime(date_format)
        return parsed_articles
