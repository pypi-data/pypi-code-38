from .base import BaseBuilder
import logging

logger = logging.getLogger(__name__)

sitemap_str = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" 
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" 
  xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
{urls}
</urlset>
"""

url_str = """  <url>
    <loc>{url}</loc>
  </url>"""

class SitemapBuilder(BaseBuilder):

    def build_sitemap(self, language, links):
        urls = set()
        site_url = self.site.url(language)
        link_attrs = self.site.link_attrs[language]
        for name in links:
          attrs = link_attrs.get(name, {})
          if not attrs.get('sitemap', True):
            logger.info("Excluding '{}' from sitemap...".format(name))
            continue
          url = self.site.full_href(language, name)
          urls.add(url_str.format(url=url))
        sitemap = sitemap_str.format(urls="\n".join(list(urls)))
        dst = self.site.get_dst('sitemap', language, extension='xml')
        self.site.write(sitemap, dst)

    def build(self):
        for language, links in self.site.links.items():
            self.build_sitemap(language, links)