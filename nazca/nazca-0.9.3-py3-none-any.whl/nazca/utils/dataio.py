# -*- coding:utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from os.path import exists as fileexists
from os import path as osp
import codecs
import json
import csv

from six import binary_type, string_types, iteritems
from six.moves import xrange
from six.moves.urllib.request import urlopen

from lxml import etree

try:
    from SPARQLWrapper import SPARQLWrapper, JSON
    SPARQL_ENABLED = True
except ImportError:
    SPARQL_ENABLED = False


###############################################################################
# UTILITY FUNCTIONS ###########################################################
###############################################################################
def autocast(data, encoding=None):
    """ Try to convert data into a specific type
    in (int, float, str)
    """
    try:
        return int(data)
    except ValueError:
        try:
            return float(data.replace(',', '.'))
        except ValueError:
            data = data.strip()
            if encoding and isinstance(data, binary_type):
                return data.decode(encoding)
            return data


###############################################################################
# RQL FUNCTIONS ###############################################################
###############################################################################
def get_cw_cnx(endpoint):
    """ Get a cnx on a CubicWeb database
    """
    from cubicweb import dbapi
    from cubicweb.__pkginfo__ import numversion
    from cubicweb.cwconfig import CubicWebConfiguration
    CubicWebConfiguration.load_cwctl_plugins()
    config = CubicWebConfiguration.config_for(endpoint)
    if numversion < (3, 19):
        sourceinfo = config.sources()['admin']
    else:
        sourceinfo = config.default_admin_config
    login = sourceinfo['login']
    password = sourceinfo['password']
    _, cnx = dbapi.in_memory_repo_cnx(config, login, password=password)
    req = cnx.request()
    return req


def rqlquery(host, rql, indexes=None, formatopt=None,
             autocast_data=True, _cache_cnx={}, **kwargs):
    """ Run the rql query on the given cubicweb host
    Additional arguments can be passed to be properly substitued
    in the execute() function for appid accces.
    """
    if host.startswith('http://'):
        # By url
        if host.endswith('/'):
            host = host[:-1]
        indexes = indexes or []
        filehandle = urlopen('%(host)s/view?'
                             'rql=%(rql)s&vid=csvexport'
                             % {'rql': rql, 'host': host})
        filehandle.readline()  # Skip the first line
        return parsefile(filehandle, delimiter=';', indexes=indexes,
                         formatopt=formatopt, autocast_data=autocast_data)
    else:
        # By appid
        if host in _cache_cnx:
            cnx = _cache_cnx[host]
        else:
            cnx = get_cw_cnx(host)
            _cache_cnx[host] = cnx
        return cnx.execute(rql, kwargs)


###############################################################################
# SPARQL FUNCTIONS ############################################################
###############################################################################
def _sparqlexecute(endpoint, query, raise_on_error=False):
    """ Execute a sparql query and return the raw results
    """
    if not SPARQL_ENABLED:
        raise ImportError("You have to install SPARQLWrapper and JSON modules to"
                          "used this function")
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        try:
            rawresults = sparql.query().convert()
            return rawresults
        except ValueError:
            # Bad json
            rawresults = sparql.query()
            return json.loads(codecs.escape_decode(
                rawresults.response.read())[0])
    except Exception as err:
        if raise_on_error:
            raise RuntimeError('Error in sparql query', err)
        else:
            return []


def sparqlquery(endpoint, query, indexes=None,
                autocast_data=True, raise_on_error=False):
    """ Run the sparql query on the given endpoint, and wrap the items in the
    indexes form. If indexes is empty, keep raw output"""
    results = []
    rawresults = _sparqlexecute(endpoint, query, raise_on_error)
    if not rawresults:
        return results
    labels = rawresults['head']['vars']
    indexes = indexes or []
    if autocast_data:
        transform = autocast
    else:
        def transform(x): return x
    for raw in rawresults["results"]["bindings"]:
        data = []
        if not indexes:
            data = [transform(raw[label]['value']) for label in labels]
        else:
            for il, ind in enumerate(indexes):
                if isinstance(ind, tuple):
                    data.append(
                        tuple([transform(raw[labels[i]]['value']) for i in ind]))
                else:
                    data.append(transform(raw[labels[il]]['value']))
        results.append(data)
    return results


def sparqljson(endpoint, query, lang_order=('fr', 'en'), raise_on_error=False):
    """ Execute and format the results of a sparql query.
    Sort the litterals using lang_order.
    """
    data = {}
    rawresults = _sparqlexecute(endpoint, query, raise_on_error)
    if not rawresults:
        return data
    results = rawresults["results"]["bindings"]
    data_lang = {}
    for row in results:
        for k, v in iteritems(row):
            if v['type'] == 'uri':
                # Uri, keep it in a set
                data.setdefault(k, set()).add(v['value'])
            elif v['type'] == 'typed-literal':
                # E.g. latitude, longitude, geometry - Keep on value
                data[k] = v['value']
            else:
                # Literal - Use lang
                data_lang.setdefault(
                    k, []).append(
                    (v['value'], v.get('xml:lang')))

    def keyfunc(x): return lang_order.index(
        x[1]) if x[1] in lang_order else len(lang_order)
    data.update(dict([(k, sorted(v, key=keyfunc)[0][0])
                      for k, v in iteritems(data_lang)]))
    return data


###############################################################################
# FILE FUNCTIONS ##############################################################
###############################################################################
def parsefile(filename, indexes=None, nbmax=None, delimiter='\t',
              encoding='utf-8', field_size_limit=None,
              autocast_data=True, formatopt=None):
    """ Parse the file (read ``nbmax`` line at maximum if given). Each
        line is splitted according ``delimiter`` and only ``indexes`` are kept

        eg : The file is :
                1, house, 12, 19, apple
                2, horse, 21.9, 19, stramberry
                3, flower, 23, 2.17, cherry

            >>> data = parsefile('myfile', [0, (2, 3), 4, 1], delimiter=',')
            data = [[1, (12, 19), u'apple', u'house'],
                    [2, (21.9, 19), u'stramberry', u'horse'],
                    [3, (23, 2.17), u'cherry', u'flower']]

            By default, all cells are "autocast" (thanks to the
            ``autocast()`` function), but you can overpass it thanks to the
            ``formatopt`` dictionnary. Each key is the index to work on, and the
            value is the function to call. See the following example:

            >>> data = parsefile('myfile', [0, (2, 3), 4, 1], delimiter=',',
            >>>                  formatopt={2:lambda x:x.decode('utf-8')})
            data = [[1, (u'12', 19), u'apple', u'house'],
                    [2, (u'21.9', 19), u'stramberry', u'horse'],
                    [3, (u'23', 2.17), u'cherry', u'flower']]

    """
    def formatedoutput(filename):
        if field_size_limit:
            csv.field_size_limit(field_size_limit)

        if isinstance(filename, string_types):
            csvfile = open(filename, 'r')
        else:
            csvfile = filename
        reader = csv.reader(csvfile, delimiter=delimiter)
        for row in reader:
            yield [cell.strip() for cell in row]
        csvfile.close()

    # Autocast if asked
    if autocast_data:
        def deffunc(x): return autocast(x, encoding)
    else:
        def deffunc(x): return x
    result = []
    indexes = indexes or []
    formatopt = formatopt or {}
    for ind, row in enumerate(formatedoutput(filename)):
        row = [formatopt.get(i, deffunc)(cell)
               for i, cell in enumerate(row)]
        data = []
        if nbmax and ind > nbmax:
            break
        if not indexes:
            data = row
        else:
            for ind in indexes:
                if isinstance(ind, tuple):
                    data.append(tuple([row[i] for i in ind]))
                    if '' in data[-1]:
                        data[-1] = None
                elif row[ind]:
                    data.append(row[ind])
                else:
                    data.append(None)

        result.append(data)
    return result


def write_results(matched, alignset, targetset, resultfile):
    """ Given a matched dictionnay, an alignset and a targetset to the
        resultfile
    """
    openmode = 'a' if fileexists(resultfile) else 'w'
    with open(resultfile, openmode) as fobj:
        if openmode == 'w':
            fobj.write('aligned;targetted;distance\n')
        for aligned in matched:
            for target, dist in matched[aligned]:
                alignid = alignset[aligned][0]
                targetid = targetset[target][0]
                fobj.write('%s;%s;%s\n' %
                           (alignid.encode('utf-8') if isinstance(alignid, string_types)
                            else alignid,
                            targetid.encode('utf-8') if isinstance(targetid, string_types)
                            else targetid,
                            dist
                            ))


def split_file(filename, outputdir, nblines=60000):
    """ Split `filename` into smaller files of ``nblines`` lines. Files are
        written into `outputdir`.

        Return the list of files
    """
    NEW = object()

    def readlines(fobj, nblines):
        """ yield all lines of the file, and
        at split-file boundaries, yield a NEW marker
        """
        for index, line in enumerate(fobj):
            if index and index % nblines == 0:
                yield NEW
            yield line

    count = 0
    with open(filename, 'rb') as fobj:
        outfile = open(osp.join(outputdir, '%s' % count), 'wb')
        for line in readlines(fobj, nblines):
            if line is NEW:
                outfile.close()
                count += 1
                outfile = open(osp.join(outputdir, '%s' % count), 'wb')
                continue
            outfile.write(line)
        outfile.close()
        count += 1
    return list(map(str, xrange(count)))


###############################################################################
# OUTPUT UTILITIES ############################################################
###############################################################################
class AbstractPrettyPrint(object):
    """ Pretty print the output of a named entities process
    """

    def pprint_text(self, text, named_entities, **kwargs):
        newtext = u''
        indice = 0
        tindices = dict([(t.start, (uri, t)) for uri, p, t in named_entities])
        while indice < len(text):
            if indice in tindices:
                uri, t = tindices[indice]
                words = text[t.start:t.end]
                fragment = self.pprint_entity(uri, words, **kwargs)
                if not self.is_valid(newtext + fragment + text[t.end:]):
                    fragment = words
                newtext += fragment
                indice = t.end
            else:
                newtext += text[indice]
                indice += 1
        return newtext

    def pprint_entity(self, uri, word, **kwargs):
        """ Pretty print an entity """
        raise NotImplementedError

    def is_valid(self, newtext):
        """Override to check the validity of the prettified content at each
        enrichement step"""
        return True


class HTMLPrettyPrint(AbstractPrettyPrint):
    """ Pretty print the output of a named entities process, in HTML
    """

    def pprint_entity(self, uri, word, **kwargs):
        """ Pretty print an entity """
        klass = ' class="%s"' % kwargs['html_class'] if 'html_class' in kwargs else ''
        return u'<a href="%s"%s>%s</a>' % (uri, klass, word)


class ValidXHTMLPrettyPrint(HTMLPrettyPrint):
    """ Pretty print the output of a named entities process,
    in valid XHTML.
    """

    XHTML_DOC_TEMPLATE = b'''\
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
<title>ner</title>
</head>
<body><div>%s</div></body>
</html>'''  # noqa

    def is_valid(self, html):
        if isinstance(html, string_types):
            html = html.encode('utf-8')
        try:
            etree.fromstring(self.XHTML_DOC_TEMPLATE % html,
                             parser=etree.XMLParser(dtd_validation=True))
        except etree.XMLSyntaxError:
            return False
        return True
