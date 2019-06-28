#!/usr/bin/env python3

import click
import time
from .wxrfile import WXRFile
from .autop import wpautop
from .wp_shortcodes import parse_shortcodes
import html2text
from .hugo_shortcodes import shortcodify
from urllib.parse import urlparse, urljoin
import json
import requests
import dateutil.parser

import os
import datetime
import hashlib
import re
import sys
from ruamel.yaml import YAML  # import yaml

yaml = YAML()
yaml.default_flow_style = False


def contains_wp_shortcodes(body, *sc):
    """Search body for one or more shortcodes named sc"""
    tagre = '|'.join(sc)
    # terrible regex taken from Wordpress source
    pattern = re.compile(
        '\\[(\\[?)(' + tagre +
        ')\\b([^\\]\\/]*(?:\\/(?!\\])[^\\]\\/]*)*?)(?:(\\/)\\]|\\](?:([^\\[]*(?:\\[(?!\\/\\2\\])[^\\[]*)*)\\[\\/\\2\\])?)(\\]?)'
    )
    if body:
        return pattern.findall(body)
    else:
        return False


def check_post_attachments(post: dict, allattach: dict):
    # Scan HTML body for <img> tags, presuming we'll download these
    if re.search(r'<img\s', post.get('body', '')):
        post['hugo_has_attachments'] = True
    # Also check for attachments known to Wordpress
    if [p for p in allattach if p.get('post_parent') == post.get('post_id')]:
        post['hugo_has_attachments'] = True
    return


def make_post_destinations(post: dict):
    post_date = post.get('post_date', datetime.datetime(1970, 1, 1, 0, 0, 0))
    fn = '{}-{}'.format(
        post_date.strftime('%Y-%m-%d'), post.get('post_name', 'UNTITLED'))
    if post.get('hugo_has_attachments'):
        filepath = os.path.join('posts', fn, 'index.md')
        bundlepath = os.path.join('posts', fn)
    else:
        filepath = os.path.join('posts', fn + '.md')
        bundlepath = None
    post['hugo_filepath'] = filepath
    post['hugo_bundlepath'] = bundlepath
    post['hugo_uniqueid'] = hashlib.md5(filepath.encode('utf-8')).hexdigest()
    return


def make_post_frontmatter(post):
    front_matter = {
        'title': post.get('title'),
        'date': post.get('post_date').isoformat(),
        'lastmod': post.get('post_date').isoformat(),
        'slug': post.get('post_name', 'UNTITLED'),
        'type': 'posts',
    }
    if post.get('excerpt'):
        front_matter['summary'] = post.get('excerpt')
    if post.get('author'):
        front_matter['author'] = post.get('author')
    if post.get('categories'):
        front_matter['categories'] = post.get('categories')
    if post.get('tags'):
        front_matter['tags'] = post.get('tags')
    if post.get('status') == 'draft':
        front_matter['draft'] = True
    post['hugo_front_matter'] = front_matter
    return


def add_resources_to_frontmatter(post: dict, allattach: dict):
    attachments = [
        p for p in allattach if p.get('post_parent') == post.get('post_id')
    ]
    if attachments:
        post['hugo_has_attachments'] = True  # redundant
        post['hugo_front_matter']['resources'] = [{
            'src':
            os.path.basename(urlparse(a.get('attachment_url')).path),
            'title':
            a.get('title')
        } for a in attachments]
        post['hugo_attachments_src'] = [
            a.get('attachment_url') for a in attachments
        ]
    return


def convert_post(post: dict):
    body = post.get('body')
    # post is HTML, so run fake wpautop on it
    body = wpautop(body)
    # Turn Wordpress shortcodes into HTML
    body = parse_shortcodes(body)
    # Parse HTML, replacing HTML attributes with Hugo shortcodes
    body, detectedhtmlimages = shortcodify(body)
    if detectedhtmlimages:
        post['hugo_has_attachments'] = True
        # add detected images to our list
        # but first, remove any that look like IMAGENAME-WWWxHHH.jpg because we probably have the original
        detectedhtmlimages = [
            a for a in detectedhtmlimages
            if not re.match(r'(.*)\-(\d+x\d+)\.(jpg|png)$', a)
        ]
        if 'hugo_attachments_src' in post:
            post['hugo_attachments_src'].extend(detectedhtmlimages)
        else:
            post['hugo_attachments_src'] = detectedhtmlimages
    # Make body into Markdown
    h = html2text.HTML2Text()
    h.images_as_html = True
    h.wrap_links = 0
    h.inline_links = 0
    body = h.handle(body).strip()
    # Un-wrap Hugo shortcodes that got line-wrapped by html2text
    body = re.sub(r'(?s)({{[\<\%].*?[\>\%]}})', lambda match: match.group(1).
                  replace('\n', ' '), body)

    parentdir, tail = os.path.split(post['hugo_filepath'])
    if not os.path.exists(parentdir):
        os.makedirs(parentdir)
    with open(post['hugo_filepath'], 'w') as f:
        f.write('---\n')
        yaml.dump(post.get('hugo_front_matter'), f)
        f.write('---\n')
        f.write(body)

    return


def download_attachments(post, blog_url):
    if post.get('hugo_bundlepath'):
        if not os.path.exists(post.get('hugo_bundlepath')):
            os.makedirs(post.get('hugo_bundlepath'))
        for u in post.get('hugo_attachments_src', []):
            fn = os.path.basename(urlparse(u).path)
            fullpath = os.path.join(post.get('hugo_bundlepath'), fn)
            # resolve relative URLs, when needed:
            u = urljoin(blog_url, u)
            r = requests.get(u, stream=True, timeout=15)
            if r.status_code == 200:
                with open(fullpath, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
                if 'last-modified' in r.headers:
                    # set file mtime to time provided by web server
                    ts = dateutil.parser.parse(
                        r.headers['last-modified']).timestamp()
                    os.utime(fullpath, (ts, ts))
            else:
                click.echo('ERROR {} on {}'.format(r.status_code, u))


def convert_comments(post):
    comments = post.get('comments')
    if comments:
        for c in comments:
            if c.get('comment_approved'):
                comment_dir = os.path.join('data', 'comments',
                                           post['hugo_uniqueid'])
                comment_fn = 'wordpress-{0:08d}.json'.format(
                    c.get('comment_id', 0))
                comment_filepath = os.path.join(comment_dir, comment_fn)
                comment_out = {}

                h = html2text.HTML2Text()
                h.wrap_links = 0

                comment_out['_id'] = hashlib.md5(
                    str(c.get('comment_id')).encode('utf-8')).hexdigest()
                if 'comment_parent' in c:
                    if c['comment_parent'] != 0:
                        comment_out['_parent'] = hashlib.md5(
                            str(c.get('comment_parent')).encode(
                                'utf-8')).hexdigest()
                    else:
                        comment_out['_parent'] = post.get('post_name')
                if post.get('post_name'):
                    comment_out['slug'] = post.get('post_name')
                comment_out['date'] = c.get(
                    'comment_date_gmt',
                    datetime.datetime(
                        1970, 1, 1, 0, 0, 0,
                        tzinfo=datetime.timezone.utc)).isoformat()
                if 'comment_author' in c:
                    comment_out['name'] = c.get('comment_author')
                if 'comment_author_email' in c:
                    comment_out['email'] = hashlib.md5(
                        c.get('comment_author_email').encode(
                            'utf-8')).hexdigest()
                if 'comment_author_url' in c:
                    comment_out['url'] = c.get('comment_author_url')
                if 'comment_content' in c:
                    # run fake wpautop on it
                    comment_body = wpautop(c['comment_content'])
                    # then convert to markdown
                    comment_out['message'] = h.handle(comment_body).strip()

                if not os.path.exists(comment_dir):
                    os.makedirs(comment_dir)
                with open(comment_filepath, 'w') as f:
                    f.write(json.dumps(comment_out, indent=2))
    return


@click.command(context_settings={'help_option_names':['-h','--help']})
@click.argument('wxr_file', type=click.Path(exists=True))
def main(wxr_file):
    """Convert a Wordpress WXR export to a Hugo site."""
    click.echo('Reading file {}...'.format(wxr_file))
    w = WXRFile(wxr_file)
    all_posts = w.get_posts()
    all_attachments = w.get_attachments()

    with click.progressbar(
            all_posts, label='Munching metadata.....', show_pos=True) as bar:
        for post in bar:
            check_post_attachments(post, all_attachments)
            make_post_destinations(post)
            make_post_frontmatter(post)
            add_resources_to_frontmatter(post, all_attachments)

    with click.progressbar(
            all_posts, label='Processing posts......', show_pos=True) as bar:
        for post in bar:
            convert_post(post)
    with click.progressbar(
            all_posts, label='Adding attachments....', show_pos=True) as bar:
        for post in bar:
            download_attachments(post, w.blog_url)
    with click.progressbar(
            all_posts, label='Converting comments...', show_pos=True) as bar:
        for post in bar:
            convert_comments(post)

    click.echo('Done.')
