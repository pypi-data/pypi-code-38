#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# dependency: python2-pycurl

import sys
import tempfile
import os
import argparse
import ConfigParser
import re

import pycurl

from mimetools import Message
from cStringIO import StringIO
from HTMLParser import HTMLParser

begins_by_known_protocol_re = re.compile("^https?://")
get_protocol_re = re.compile("^([a-z]+)://")

def checkWebpageHttpCacheHit(url_list, resolve_list=[], cookie_jar_path=None):
  report_line_list = []
  class MyHTMLParser(HTMLParser):
    def __init__(self, base_url):
      HTMLParser.__init__(self)
      self.base_url = base_url
    def handle_starttag(self, tag, attrs):
      def handle_url(url):
        if url.startswith("//"):
          protocol = get_protocol_re.match(self.base_url)
          if protocol is not None:
            protocol = protocol.group(1)
          else:
            protocol = "http"
          url = protocol + ":" + url
        elif begins_by_known_protocol_re.match(url) is None:
          url = self.base_url + ("" if self.base_url.endswith("/") else "/") + url
        do_request(url)
      # handle images and js scripts
      if tag == 'img' or tag == 'script':
        for attr in attrs:
          if attr[0] == 'src':
            handle_url(attr[1])
      # handle css and favicon
      if tag == 'link' and \
         any(attr[0] == "rel" and attr[1] in ("stylesheet", "shortcut icon") for attr in attrs):
        for attr in attrs:
          if attr[0] == "href":
            handle_url(attr[1])

  headers = {
    "User-Agent": "test",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    # "Connection": "keep-alive"
  }

  parsed_url_dict = set()
  def do_request(url):
    if url in parsed_url_dict: return
    parsed_url_dict.add(url)
    print("Checking cache hit for " + url)
    c = pycurl.Curl()
    response_headers = StringIO()
    output = StringIO()
    c.setopt(c.URL, url)
    c.setopt(c.RESOLVE, resolve_list)
    c.setopt(c.WRITEFUNCTION, output.write)
    c.setopt(c.HEADERFUNCTION, response_headers.write)
    c.setopt(c.COOKIEFILE, cookie_jar_path)
    c.setopt(c.COOKIEJAR, cookie_jar_path)
    try:
      c.perform() # perform a request before testing if the cache is hit
      response_headers.truncate(0)
      output.truncate(0)
      c.perform()
      if str(c.getinfo(pycurl.HTTP_CODE))[0:1] != "2":
        if c.getinfo(pycurl.HTTP_CODE) >= 400:
          report_line_list.append("Status code %s received for %s" % (c.getinfo(pycurl.HTTP_CODE), url))
        else:
          print("Status code %s not handled" % c.getinfo(pycurl.HTTP_CODE))
        return
    except pycurl.error as e:
      if e[0] == 6: # Could not resolve domain
        report_line_list.append(e[1])
        return
      raise

    response_headers.seek(0)
    status = response_headers.readline().split(" ")[1]

    m = Message(response_headers)

    # see http://labs.omniti.com/people/mark/ats_sa/slides.html#slide-18
    if not any("[cHs" in header for header in m.getheaders('via')) and \
       not any("HIT" in header for header in m.getheaders("x-cache")):
      report_line_list.append("No cache hit found for " + url)
      # report_line_list.append(response_headers.getvalue().rstrip())

    if m.getheader("content-type", "").startswith("text/html"):
      MyHTMLParser(url).feed(output.getvalue())

    response_headers.close()
    output.close()

  for url in url_list:
    do_request(url)

  if report_line_list == []:
    print("No failure.")
    return True
  print("Failure report:")
  for line in report_line_list:
    print("- " + line)
  return False

def getConfig(config_parser, section, option, default=None, raw=False, vars=None):
  try:
    return config_parser.get(section, option, raw=raw, vars=vars)
  except ConfigParser.NoOptionError:
    return default

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-K", "--config", nargs=1, metavar="FILE", help="read config from FILE")
  parser.add_argument("-c", "--cookie-jar", nargs=1, metavar="FILE", help="write cookies to FILE after operation")
  parser.add_argument("--resolve", nargs="+", default=[], metavar="HOST:PORT:ADDRESS", help="force resolve of HOST:PORT to ADDRESS")
  parser.add_argument("url-list", nargs="*", metavar="URL", default=[])
  args = parser.parse_args()
  args.url_list = getattr(args, "url-list")

  if args.config is not None:
    parser = ConfigParser.ConfigParser()
    parser.read(args.config)
    if args.url_list == []:
      args.url_list = getConfig(parser, "public", "url-list", "").split()
    if args.resolve == []:
      args.resolve = getConfig(parser, "public", "resolve-list", "").split()
    if args.cookie_jar is not None:
      args.cookie_jar = getConfig(parser, "public", "cookie-jar-filename", "")
      if args.cookie_jar == "":
        args.cookie_jar = None

  if args.url_list == []:
    raise ValueError("No url to check")

  if args.cookie_jar is None:
    cookie_jar = tempfile.NamedTemporaryFile(delete=False)
    cookie_jar_path = cookie_jar.name
    cookie_jar.close()
  else:
    cookie_jar_path = args.cookie_jar
  try:
    res = checkWebpageHttpCacheHit(args.url_list, args.resolve, cookie_jar_path)
  finally:
    if args.cookie_jar is None:
      os.unlink(cookie_jar_path)
  return 0 if res else 1

if __name__ == "__main__":
  sys.exit(main())
