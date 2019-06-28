from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import re

def shortcodify(body: str):
    """Replace post-body HTML with Hugo shortcodes when possible."""
    soup = BeautifulSoup(body, 'html.parser')
    images_src = []
    
    # <figure> -> {{% figure %}}
    for fig in soup('figure'):
        link = fig.find('a')
        href = None
        caption = None
        src = None
        if link:
            # This image is wrapped in a link
            href = link.get('href')
            link.unwrap() # remove link but keep contents
        img = fig.find('img')
        if img:
            src = img.get('src')
            images_src.append(src) # add to our list
            if os.path.basename(urlparse(src).path):
                # the IMG SRC is a file, so let's just use the filename sans path
                src = os.path.basename(urlparse(src).path)
                src = re.sub(r'(.*)\-(\d+x\d+)\.(jpg|png)$', r'\1.\3', src)
        figcaption = fig.find('figcaption')
        if figcaption:
            caption = figcaption.text

        shortcode = '{{% figure'
        if src:
            shortcode += ' src="{}"'.format(src)
        if href:
            shortcode += ' link="{}"'.format(href)
        if caption:
            shortcode += ' caption="{}"'.format(caption)

        shortcode += ' %}}'
        fig.insert_before(shortcode)
        fig.decompose() # destroy original figure tag

    # <img> -> {{% img %}}
    # Also maps Wordpress class="alignright" to class="float-right", etc. 
    for img in soup('img'):
        link = img.findParent('a')
        href = None
        if link:
            # This image is wrapped in a link
            href = link.get('href')
            link.unwrap() # remove link but keep contents
        src = img.get('src')
        images_src.append(src) # add to our list
        alt = img.get('alt')
        if os.path.basename(urlparse(src).path):
            # the IMG SRC is a file, so let's just use the filename sans path
            src = os.path.basename(urlparse(src).path)
            src = re.sub(r'(.*)\-(\d+x\d+)\.(jpg|png)$', r'\1.\3', src)
        shortcode = '{{% img'
        shortcode += ' src="{}"'.format(src) if src else ''
        if alt:
            shortcode += ' alt="{}"'.format(alt)
        if href:
            shortcode += ' link="{}"'.format(href)
        if 'alignright' in img.get('class', []):
            shortcode += ' class="float-right"'
        if 'alignleft' in img.get('class', []):
            shortcode += ' class="float-left"'
        shortcode += ' %}}'
        img.insert_before(shortcode)
        img.decompose() # destroy original img tag

    # <blockquote> -> {{% blockquote %}}
    for bq in soup('blockquote'):
        cite = bq.cite
        if cite:
            citation = cite.extract().decode_contents()
        shortcode = '{{% blockquote'
        if cite:
            shortcode += ' source="{}"'.format(citation.replace('"', '&quot;'))
        shortcode += ' %}}\n'
        bq.insert_before(shortcode)
        bq.insert_after('\n{{% /blockquote %}}')
        bq.unwrap() # destroy original blockquote tag

    return str(soup), images_src