#!/usr/bin/env python
# coding=utf-8
"""
use encoding utf-8
"""
from __future__ import print_function

import concurrent
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor

import deepcut
import requests

from datasketch import MinHash


def mygrouper(n, iterable):
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in itertools.zip_longest(*args))


def tokenize(str):
    """
    Tokenize given Thai, English text string
    Args:
       str - Required : Thai, English, Mix(Thai,English) text string
    Returns:
       tokens: list, list of tokenized words
    Example
    >> sixecho.tokenize('I am a developer python newly. ผมเป็นมือใหม่สำหรับ python')
    >> ['I','am','a','developer','python','newly','.','ผม','เป็น','มือ','ใหม่','สำหรับ','python']
    """
    words = deepcut.tokenize(str)
    new_words = [word for word in words if word != ' ']
    return new_words


def tokenize_mutiline(lines=[]):
    result = []
    if len(lines) == 0:
        return result
    with ThreadPoolExecutor(max_workers=len(lines)) as executor:
        future_to_url = {
            executor.submit(tokenize, line): line
            for line in lines
        }
        for future in concurrent.futures.as_completed(future_to_url):
            data = future.result()
            result = result + data
        return result


def printProgressBar(iteration,
                     total,
                     prefix='Progress',
                     suffix='Complete',
                     decimals=1,
                     length=100,
                     fill='='):
    """
    Call in a loop to create terminal progress bar
    Args:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    tab_bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, tab_bar, percent, suffix), end="\r")
    # Print New Line on Complete
    if iteration == total:
        print()


class Client(object):
    """
    client class to control api with restful
    """

    def __init__(self,
                 api_key=None,
                 host_url=None,
                 max_workers=1,
                 meta_books=None):
        """
        Initial sixecho
        Attributes:
            api_key(string)       - Optional : api_key generate from sixecho
            host_url(string)      - Optional : is sixecho domain
            meta_books(Hash)      - Require  : struct books include
                - category_id(string) - Require : category of books you can get from search category api
                - publisher_id(string) - Require : publisher of book you can get from search publisher api
                - title(string) - Require : title book
                - auther(string) - Require : auther book
                - country_of_origin(string) : country iso 3166-1 
                - language(string) Require : language iso 639-1  
                - paperback(string) Require : total page book
                - publish_date(string) Require : publish date
        """
        self.api_key = api_key
        deepcut.tokenize("Welcome")  # Load library
        if host_url is not None:
            if host_url.endswith("/"):
                host_url = host_url[:-1]
            self.host_url = host_url
        self.array_words = []
        self.min_hash = MinHash(num_perm=128)
        self.max_workers = max_workers
        self.sha256 = ""
        self.fileSize = 0
        self.meta_books = meta_books

    def digest(self):
        """Export the hash values, which is the internal state of the
        MinHash.

        Returns:
            numpy.array: The hash values which is a Numpy array.
        """
        return self.min_hash.digest()

    def generate(self, str=None, fpath=None):
        """Generate minhash with new value from string or file
        we use minhash from https://ekzhu.github.io/datasketch/_modules/datasketch/minhash.html#MinHash.update
        Args:
            str(string)     - Optional  :   string whose minhash to be computed.
            fpath(string)   - Optional  :   path file to be computed.
        """
        if fpath:
            self.load_file(fpath)
        else:
            sha256 = hashlib.sha256()
            sha256.update(str)
            self.sha256 = sha256.hexdigest()
            self.array_words = tokenize(str)
            self.fileSize = len(str)
            for d in self.array_words:
                self.min_hash.update(d.encode('utf8'))

    def upload(self):
        """Upload digital conent to server

        """
        digest = ",".join([str(num) for num in self.digest()])
        if self.host_url is None or self.api_key is None:
            raise Exception("Require host_url and api_key")

        headers = {
            "x-api-key": self.api_key,
            'content-type': 'application/json'
        }
        response = requests.post(
            (self.host_url + "/checker"),
            json={
                "digest": digest,
                "sha256": self.sha256,
                "size_file": self.fileSize,
                "meta_books": self.meta_books
            },
            headers=headers)
        print("content:" + str(response.text))
        return json.loads(response.text)

    def load_file(self, fpath):
        """
        method load_file
        """
        sha256 = hashlib.sha256()
        f_count = open(fpath, "r")
        f = f_count.readlines()
        f_count.close()
        list_of_groups = None
        if self.max_workers != 1:
            l = f
            n = self.max_workers
            list_of_groups = [l[i:i + n] for i in range(0, len(l), n)]
            #  list_of_groups = zip(*(iter(f), ) * self.max_workers)

        fileSize = os.path.getsize(fpath)
        printProgressBar(0,
                         fileSize,
                         prefix='Progress:',
                         suffix='Complete',
                         length=50)
        progress = 0
        lines = []
        if self.max_workers == 1:
            for line in f:
                progress = progress + len(line)
                sha256.update(line)
                words = tokenize(line)
                if len(words) != 0:
                    for d in words:
                        self.min_hash.update(d.encode('utf8'))
                printProgressBar(progress,
                                 fileSize,
                                 prefix='Progress:',
                                 suffix='Complete',
                                 length=50)
        else:
            for line in f:
                sha256.update(line)
            for lines in list_of_groups:
                for line in lines:
                    progress = progress + len(line)
                    #  sha256.update(line)
                words = tokenize_mutiline(lines)
                if len(words) != 0:
                    for d in words:
                        self.min_hash.update(d.encode('utf8'))
                printProgressBar(progress,
                                 fileSize,
                                 prefix='Progress:',
                                 suffix='Complete',
                                 length=50)
        self.sha256 = sha256.hexdigest()
        self.fileSize = fileSize
        #  for line in f:
        #  progress = progress + len(line)
        #  sha256.update(line)
        #  words = []
        #  loop_i = loop_i + 1
        #  if self.max_workers == 1:
        #  words = tokenize(line)
        #  else:
        #  if len(lines) == self.max_workers or (loop_i == line_count):
        #  if loop_i == line_count:
        #  lines.append(line)
        #  print(line)
        #  print(str(loop_i) + " " + str(len(lines)))
        #  words = tokenize_mutiline(lines)
        #  lines = []
        #  else:
        #  lines.append(line)
        #  if len(words) != 0:
        #  for d in words:
        #  self.min_hash.update(d.encode('utf8'))
        #  printProgressBar(progress,
        #  fileSize,
        #  prefix='Progress:',
        #  suffix='Complete',
        #  length=50)
        #  self.sha256 = sha256.hexdigest()
