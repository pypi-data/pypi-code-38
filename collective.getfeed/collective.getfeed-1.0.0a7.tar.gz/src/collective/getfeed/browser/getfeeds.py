# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from collective.getfeed import logger
from DateTime import DateTime
from datetime import datetime
from io import BytesIO
from lxml.cssselect import CSSSelector
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser import BrowserView
from urllib2 import Request
from urllib2 import URLError
from urllib2 import urlopen
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import feedparser
import htmlentitydefs
import json
import lxml.html
import re
import requests
import time
import transaction


HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


class GetFeedsView(BrowserView):
    """Process feeds."""

    def unescape(self, text):
        def fixup(m):
            text = m.group(0)
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text
        return re.sub("&#?\w+;", fixup, text)

    def _feedItemsToNews(self, item, feedName):
        if not item:
            return
        portal = api.portal.get()
        pt = portal.portal_transforms
        putils = portal.plone_utils
        dictNews = {'id': '',
                    'title': '',
                    'description': '',
                    'text': '',
                    'subjects': [],
                    'creators': [],
                    'rights': '',
                    'source': '',
                    'effectiveDate': '',
                    'creation_date': ''}

        now = datetime.now().timetuple()
        dictNews['title'] = item.get('title', '')
        # id deve ser uma string
        entry_id = str(putils.normalizeString('%s' % dictNews['title']))
        if entry_id in self.context.objectIds():
            # Content already there, ignore it
            return {}
        dictNews['id'] = entry_id
        description = item.get('summary', '')
        text = '<div></div>'
        content = item.get('content', [{}, ])
        if 'value' in content[0] and content[0].value:
            text = content[0].value
        description_type = item.get('summary_detail', {}).get('type',
                                                              'text/plain')
        # Convert br tags to line breaks
        description = description.replace('<br />', '\n').encode('utf-8')
        description = pt.convertTo('text/plain', description,
                                   mimetype=description_type).getData()
        description = description.replace('&nbsp;', ' ')
        description = description.strip()
        if description:
            # If we have multiple paragraphs, get just the first one
            description = [l.strip() for l in description.split('\n')
                           if l.strip()][0]
        dictNews['description'] = self.unescape(description).decode('utf-8')
        dictNews['text'] = text
        image = self._image_from_body(text)
        if not image:
            # Try to get image from description
            image = self._image_from_body(item.get('summary', ''))
        if image:
            dictNews['image'] = image
            dictNews['image_caption'] = ''
        tags = item.get('tags', []) and [tag.get('term', '')
                                         for tag in item.get('tags', [])] or []
        dictNews['subjects'] = tags
        dictNews['creators'] = tuple([item.get('author', '') or feedName])
        dictNews['rights'] = feedName
        creation_date = (item.get('created_parsed', '') or
                         item.get('published_parsed', '') or
                         item.get('updated_parsed', now))
        dictNews['creation_date'] = DateTime(
            creation_date and time.strftime('%Y-%m-%d %H:%M', creation_date))
        effectiveDate = item.get('published_parsed', '') or creation_date
        dictNews['effective_date'] = DateTime(
            effectiveDate and time.strftime('%Y-%m-%d %H:%M', effectiveDate))
        dictNews['anexos'] = item.get('enclosures', [])
        dictNews['url'] = item.get('feedburner_origlink',
                                         item.get('link', ''))
        if not dictNews['id']:
            dictNews = None
        return dictNews

    def _image_from_body(self, text):
        """ Get the first image from entry body """
        if not text:
            return None
        dom = lxml.html.fromstring(text)
        selAnchor = CSSSelector('img')
        foundElements = selAnchor(dom)
        links = [e.get('src') for e in foundElements]
        if links:
            link = links[0]
            req = Request(link.encode('utf-8'), headers=HDR)
            try:
                fh = urlopen(req)
            except URLError:
                # Not able to open the link
                # return an empty image
                return None
            data = fh.read()
            content_type = fh.headers['content-type']
            return (data, content_type)

    def _objFromUID(self, uid):
        """ Return a object from an UID """
        ct = self._ct
        results = ct.searchResults(UID=uid)
        if results:
            obj = results[0].getObject()
            return obj

    def create_entry(self, folder, dictNews):
        """ Create item """
        oId = str(dictNews.get('id'))
        if oId not in folder.objectIds():
            _createObjectByType('Feed Item', folder, id=oId,
                                title=dictNews.get('title'),
                                description=dictNews.get('description'))
        else:
            return folder[oId]
        logger.info('     - Create item %s' % (oId))
        o = folder[oId]
        if not o:
            return
        for k, v in dictNews.items():
            if k in ['title', 'id', 'anexos']:
                continue
            if k in ['text']:
                v = RichTextValue(v, 'text/html', 'text/html')
                o.text = v
            if k in ['image']:
                data = v[0]
                content_type = v[1]
                filename = u'image.%s' % (content_type.split('/')[1])
                v = NamedBlobImage(data, content_type, filename)
                o.image = v
            if v and hasattr(o, k):
                setattr(o, k, v)
        o.exclude_from_nav = True

        with api.env.adopt_roles(['Manager']):
            api.content.transition(obj=o, transition='publish')
        o.reindexObject()
        return o

    def execute(self):
        """ Process feeds, create objects """
        summary = {'feeds': 0, 'entries': 0}
        summary['feeds'] = 1
        feedName = self.context.Title()

        try:
            resp = requests.get(self.context.url, timeout=10)
        except requests.ReadTimeout:
            logger.warn("Timeout when reading RSS %s", rss_feed)
            return

        content = BytesIO(resp.content)
        feed = feedparser.parse(content)
        if feed.bozo:
            logger.info(feed['bozo_exception'].message)

        if hasattr(feed, 'entries'):
            old_entries = self.context.objectIds()
            items = feed.entries
            logger.info('Feed %s processed: %d items' %
                     (feedName, len(items)))
            itemsDates = []
            for item in items:
                dictNews = self._feedItemsToNews(item,
                                                 feedName)
                if not dictNews:
                    # Already processed
                    logger.info('     - Item already processed')
                    continue
                date = DateTime(dictNews['creation_date'])
                summary['entries'] = summary['entries'] + 1
                itemsDates.append(date)
                self.create_entry(self.context, dictNews)
                try:
                    old_entries.remove(str(dictNews.get('id')))
                except ValueError:
                    pass
            for entry in old_entries:
                api.content.delete(obj=self.context.get(entry))

            if itemsDates:
                # Registra nova data
                itemsDates.sort()
        return summary

    def __call__(self):
        if api.user.is_anonymous():
            return
        alsoProvides(self.request, IDisableCSRFProtection)
        response = self.request.response
        response.setHeader('content-type', 'application/json')
        return response.setBody(json.dumps(self.execute()))


class GetAllFeedsView(BrowserView):
    """Process all feeds."""

    def execute(self):
        summary = {'feeds': 0, 'entries': 0}
        catalog = api.portal.get_tool('portal_catalog')
        query = dict(
            portal_type='Feed',
            review_state='published'
        )
        results = catalog.searchResults(**query)
        inicio = datetime.now()
        logger.info('Start {0}'.format(inicio.strftime('%Y-%m-%d %H:%M:%S')))
        for brain in results:
            blog = brain.getObject()
            view = blog.restrictedTraverse('@@get-feeds')
            summary_feed = view.execute()
            summary['feeds'] += summary_feed['feeds']
            summary['entries'] += summary_feed['entries']
            logger.info('{}, {}'.format(blog.Title(), summary_feed))
        transaction.commit()
        termino = datetime.now()
        logger.info('Take {0} segunds'.format((termino - inicio).seconds))
        return summary

    def __call__(self):
        if api.user.is_anonymous():
            return
        alsoProvides(self.request, IDisableCSRFProtection)
        response = self.request.response
        response.setHeader('content-type', 'application/json')
        return response.setBody(json.dumps(self.execute()))
