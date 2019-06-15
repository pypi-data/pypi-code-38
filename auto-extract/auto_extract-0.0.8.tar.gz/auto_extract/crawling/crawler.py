import re
import time
import urllib.robotparser
import urllib.request
import requests
import lxml.html
from auto_extract import Article
from auto_extract.utils import extract_domain
from auto_extract.crawling.storage import Storage
from auto_extract.crawling.regexes import make_regex
from auto_extract.crawling.block import should_be_blocked


def remove_hash_after_last_dash(article_url):
    return re.sub("-[a-f]*[0-9]+[a-f]+[0-9]+[a-f0-9]+$", "", article_url)


file_extensions = set([".jpg", ".png", ".zip", ".dmg", ".exe", ".gz"])


class UpfrontRobotFileParser(urllib.robotparser.RobotFileParser):
    def read(self, as_user_agent):
        try:
            r = requests.get(self.url, headers={"User-Agent": as_user_agent}, timeout=1)
            if r.status_code in (401, 403):
                self.disallow_all = True
            elif r.status_code >= 400 and r.status_code < 500:
                self.allow_all = True
            else:
                self.parse(r.text.splitlines())
        except:
            self.allow_all = True


class Crawler(object):
    def __init__(
        self,
        seed_urls,
        name,
        info_type,
        all_required_regexes=None,
        any_exclude_regexes=None,
        url_xpath="//a/@href",
        remove_query_param=True,
        get_id=remove_hash_after_last_dash,
        notify=lambda articles, crawler: None,
        add_query_param_nonce=False,
        auto_detect_fn=None,
    ):
        self.user_agent = "Upfrontbot/1.0 (+https://www.upfront.ai/)"
        self.headers = {"User-Agent": self.user_agent}
        self.seed_urls = seed_urls if isinstance(seed_urls, list) else [seed_urls]
        self.storage = Storage(name, notify=lambda articles: notify(articles, self))
        self.name = name
        self.info_type = info_type
        self.domain_names, self.domains = [], []
        self.robot_parsers = []
        self.setup_seeds(seed_urls)
        all_required_regexes = all_required_regexes or []
        self.all_required_regexes = [make_regex(x) for x in all_required_regexes]
        any_exclude_regexes = any_exclude_regexes or []
        self.any_exclude_regexes = [make_regex(x) for x in any_exclude_regexes]
        self.url_xpath = url_xpath
        self.remove_query_param = remove_query_param
        self.get_id = get_id
        self.s = requests.Session()
        self.s.headers.update(self.headers)
        self.add_query_param_nonce = add_query_param_nonce
        # auto_detect_fn is a function applied on all urls returning a verification regex
        self.auto_detect_fn = auto_detect_fn
        self.seed_error = 0

    def setup_seeds(self, seed_urls):
        for seed_url in seed_urls:
            if not seed_url:
                continue
            if any(
                [
                    x in seed_url.split("/")[2]
                    for x in ["tumblr", "ink.one"]
                    if len(seed_url.split("/")) > 2
                ]
            ):
                continue
            domain_name, domain = extract_domain(seed_url)
            self.domain_names.append(domain_name)
            self.domains.append(domain)
            self.robot_parsers.append(self.get_robo_parser_domain(domain))

    def get_robo_parser_domain(self, domain):
        rp = UpfrontRobotFileParser()
        robot_url = urllib.request.urljoin(domain, "robots.txt")
        rp.set_url(robot_url)
        try:
            rp.read(self.user_agent)
        except Exception as e:
            print(e)

            class rp:
                def can_fetch(self, user_agent, url):
                    return True

        return rp

    def robots_can_fetch(self, url):
        for robot_parser in self.robot_parsers:
            if robot_parser.can_fetch(self.user_agent, url):
                return True
        return False

    @property
    def invalid_seeds(self):
        return self.seed_error == len(self.seed_urls)

    def within_domain(self, url):
        parts = url.split("/")
        if len(parts) < 3:
            return False
        return any([domain_name in url.split("/")[2] for domain_name in self.domain_names])

    def get(self, url):
        try:
            response = self.s.get(url, timeout=3)
        except:
            return None
        if response.status_code > 399:
            return None
        return response.content

    def pre_process_url(self, url):
        if self.remove_query_param:
            url = url.split("?")[0]
        return url

    def view_tree(self):
        from requests_viewer import view_tree

        for seed_url in self.seed_urls:
            view_tree(lxml.html.fromstring(self.get(seed_url)))

    def return_seed_url_with_query_nonce(self, seed_url):
        semi_random_nonce = str(int(time.time()))
        separator = "&" if "?" in seed_url else "?"
        return seed_url + separator + "additionals_param=" + semi_random_nonce

    def get_links(self):
        links = {}
        self.seed_error = 0
        for seed_url, domain in zip(self.seed_urls, self.domains):
            if self.add_query_param_nonce:
                seed_url = self.return_seed_url_with_query_nonce(seed_url)
            content = self.get(seed_url)
            if content is None:
                print("no content in seed_url {}".format(seed_url))
                self.seed_error += 1
                continue
            tree = lxml.html.fromstring(content)
            tree.make_links_absolute(domain)
            web_urls = tree.xpath(self.url_xpath)
            if self.auto_detect_fn:
                auto_pattern = self.auto_detect_fn(web_urls)
            for link in web_urls:
                link = self.pre_process_url(link)
                if not link:
                    continue
                link_id = self.get_id(link)
                if link_id in self.storage.seen:
                    continue
                if not self.within_domain(link):
                    continue
                if should_be_blocked(link):
                    continue
                if link == seed_url:
                    continue
                if any([link.endswith(x) for x in file_extensions]):
                    continue
                if not self.robots_can_fetch(link):
                    continue
                if self.any_exclude_regexes and any(
                    [x.search(link) for x in self.any_exclude_regexes]
                ):
                    continue
                if self.all_required_regexes and not all(
                    [x.search(link) for x in self.all_required_regexes]
                ):
                    continue
                if self.auto_detect_fn and auto_pattern and not auto_pattern.search(link):
                    continue
                self.storage.seen.add(link_id)
                links[link_id] = link
        return links

    def save_articles_from_links(self, links):
        articles = []
        for link_id, link in links.items():
            article = Article.from_url(link, self.s)
            article.id = link_id
            articles.append(article)
        return self.storage.add_articles(articles)

    def start(self):
        num_new = self.save_articles_from_links(self.get_links())
        return num_new


# Crawler("http://iex.ec", "test", "currency").get_links()
