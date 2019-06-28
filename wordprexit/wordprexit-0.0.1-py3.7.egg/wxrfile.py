import re
import datetime
from urllib.parse import urlparse
from xml.etree import ElementTree
import pytz
import tzlocal

def parse_pubdate(datestr):
    # Draft posts often have a date year of -0001. Awesome.
    datestr = re.sub(r'\+000$', '+0000', datestr)
    datestr = re.sub(r'-0001', '1970', datestr)
    return datetime.datetime.strptime(datestr, '%a, %d %b %Y %H:%M:%S %z')


class WXRFile(object):
    def __init__(self, input_file, blog_timezone=None):
        self.input_file = input_file
        # Parse once to fetch XML namespaces
        self.namespaces = dict([
            node for _, node in ElementTree.iterparse(
                input_file, events=['start-ns'])
        ])
        # Parse again to build tree
        self.tree = ElementTree.parse(input_file)
        self.blog_title = self.tree.find('channel').findtext('title')
        self.blog_url = self.tree.find('channel').findtext('link')
        self.blog_hostname = urlparse(
            self.tree.find('channel').findtext('link')).hostname
        self.blog_language = self.tree.find('channel').findtext('language')

        # Allow users to override timezone
        if blog_timezone:
            self.blog_timezone = pytz.timezone(blog_timezone)
        else:
            self.blog_timezone = tzlocal.get_localzone()

    def get_attachments(self):
        return [
            i for i in self.get_items() if i.get('post_type') == 'attachment'
        ]

    def get_nav_menu_items(self):
        return [
            i for i in self.get_items()
            if i.get('post_type') == 'nav_menu_item'
        ]

    def get_pages(self):
        return [i for i in self.get_items() if i.get('post_type') == 'page']

    def get_posts(self):
        return [i for i in self.get_items() if i.get('post_type') == 'post']

    def get_items(self):
        for post in self.tree.find('channel').findall('item'):
            out = {}

            inputs = [
                ('title', 'title'),
                ('link', 'link'),
                ('pubDate', 'pubDate'),
                ('content:encoded', 'body'),
                ('excerpt:encoded', 'excerpt'),
                ('wp:post_id', 'post_id'),
                ('wp:post_date', 'post_date'),
                ('wp:post_date_gmt', 'post_date_gmt'),
                ('wp:post_name', 'post_name'),
                ('wp:status', 'status'),
                ('wp:comment_status', 'comment_status'),
                ('wp:post_type', 'post_type'),
                ('wp:post_parent', 'post_parent'),
                ('wp:attachment_url', 'attachment_url'),
                ('dc:creator', 'author'),
            ]
            for a, b in inputs:
                if post.findtext(a, namespaces=self.namespaces):
                    out[b] = post.findtext(
                        a, namespaces=self.namespaces).strip()

            if 'pubDate' in out:
                out['pubDate'] = parse_pubdate(out['pubDate'])
            if 'post_date' in out:
                out['post_date'] = self.blog_timezone.localize(datetime.datetime.strptime(out.get('post_date')[:19], '%Y-%m-%d %H:%M:%S'))
            if 'post_date_gmt' in out:
                if out['post_date_gmt'].startswith('0000'):
                    out['post_date_gmt'] = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
                else:
                    out['post_date_gmt'] = datetime.datetime.strptime(out.get('post_date_gmt')[:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            if 'post_id' in out:
                out['post_id'] = int(out['post_id'])
            if 'post_parent' in out:
                out['post_parent'] = int(out['post_parent'])

            postmeta = {}
            for m in post.findall('wp:postmeta', namespaces=self.namespaces):
                k = m.findtext('wp:meta_key', namespaces=self.namespaces)
                v = m.findtext('wp:meta_value', namespaces=self.namespaces)
                postmeta[k] = v

            if postmeta:
                out['postmeta'] = postmeta

            categories = []
            tags = []
            for c in post.findall('category'):
                if c.get('domain') == 'category':
                    categories.append(c.text)
                elif c.get('domain') == 'post_tag':
                    tags.append(c.text)
                elif c.get('domain') == 'post_format':
                    # for some reason post_format is encoded as a category
                    out['post_format'] = c.get('nicename').replace('post-format-', '')

            if categories:
                out['categories'] = categories
            if tags:
                out['tags'] = tags

            comments = []
            for c in post.findall('wp:comment', namespaces=self.namespaces):
                comment = {}
                comment_inputs = [('wp:comment_id', 'comment_id'),
                                  ('wp:comment_author', 'comment_author'),
                                  ('wp:comment_author_email',
                                   'comment_author_email'),
                                  ('wp:comment_author_url',
                                   'comment_author_url'),
                                  ('wp:comment_author_IP',
                                   'comment_author_IP'),
                                  ('wp:comment_date', 'comment_date'),
                                  ('wp:comment_date_gmt', 'comment_date_gmt'),
                                  ('wp:comment_content', 'comment_content'),
                                  ('wp:comment_approved', 'comment_approved'),
                                  ('wp:comment_type', 'comment_type'),
                                  ('wp:comment_parent', 'comment_parent'),
                                  ('wp:comment_user_id', 'comment_user_id')]
                for a, b in comment_inputs:
                    if c.findtext(a, namespaces=self.namespaces):
                        comment[b] = c.findtext(
                            a, namespaces=self.namespaces).strip()

                if 'comment_date' in comment:
                    comment['comment_date'] = datetime.datetime.strptime(
                        comment['comment_date'], '%Y-%m-%d %H:%M:%S')
                if 'comment_date_gmt' in comment:
                    comment['comment_date_gmt'] = datetime.datetime.strptime(
                        comment['comment_date_gmt'],
                        '%Y-%m-%d %H:%M:%S').replace(
                            tzinfo=datetime.timezone.utc)
                if 'comment_approved' in comment:
                    comment['comment_approved'] = bool(
                        comment['comment_parent'])
                if 'comment_id' in comment:
                    comment['comment_id'] = int(comment['comment_id'])
                if 'comment_parent' in comment:
                    comment['comment_parent'] = int(comment['comment_parent'])
                if 'comment_user_id' in comment:
                    comment['comment_user_id'] = int(
                        comment['comment_user_id'])
                comments.append(comment)

            if comments:
                out['comments'] = comments

            yield out
