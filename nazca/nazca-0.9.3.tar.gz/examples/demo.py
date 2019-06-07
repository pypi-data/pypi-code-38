#!/usr/bin/python
#-*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from os import path

import six.moves.urllib.request, six.moves.urllib.parse, six.moves.urllib.error

import nazca.distances as ald
import nazca.normalize as aln
from nazca.aligner import align, subalign, findneighbours, alignall
from nazca.dataio import parsefile, sparqlquery, write_results

DEMODIR = path.dirname(__file__)

def dpath(filename):
    return path.join(DEMODIR, 'demo', filename)

def remove_after(string, sub):
    try:
        return string[:string.lower().index(sub)].strip()
    except ValueError:
        return string

def parserql(host, rql):
    filehandle = six.moves.urllib.request.urlopen('%(host)sview?'
                                'rql=%(rql)s&vid=csvexport'
                                % {'rql': rql, 'host': host})
    filehandle.readline()
    rset = [[e.decode('utf-8') for e in line.strip().split(';')]
            for line in filehandle]
    return rset

def demo_0():
    # prixgoncourt is the list of Goncourt Prize, extracted
    # from wikipedia

    #We try to align Goncourt winers onto dbpedia results

    query = """
       SELECT ?writer, ?name WHERE {
          ?writer  <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:French_novelists>.
          ?writer rdfs:label ?name.
          FILTER(lang(?name) = 'fr')
       }
    """

    print("Sending query to dbpedia")
    targetset = sparqlquery('http://dbpedia.org/sparql', query)
    print("Reading the prixgoncourt file")
    alignset = parsefile(dpath('prixgoncourt'), indexes=[1, 1])

    tr_name = {'normalization': [lambda x:remove_after(x, '('),
                                 aln.simplify],
               'metric': ald.levenshtein
              }

    processings = {1: tr_name}

    print("Alignment started")
    align(alignset, targetset, 0.4, processings,
          dpath('demo0_results'))

    print("Done, see the resuls in %s" % dpath('demo0_results'))

def demo_1():
    # FR.txt is an extract of geonames, where locations have been sorted by name
    # frenchbnf is an extract of french BNF's locations, sorted by name too

    # For each line (ie location) we keep the identifier, the name and the
    # position (longitude, latitude)
    # ``nbmax`` is the number of locations to load

    print("Parsing the input files")
    targetset = parsefile(dpath('FR.txt'), indexes=[0, 1, (4, 5)],
                          nbmax=2000)
    alignset = parsefile(dpath('frenchbnf'),
                         indexes=[0, 2, (14, 12)], nbmax=1000)


    # Let's define the processings to apply on the location's name
    tr_name = {'normalization': [aln.simplify], # Simply all the names (remove
                                              #   punctuation, lower case, etc)
               'metric': ald.levenshtein,       # Use the levenshtein distance
               'weighting': 1                 # Use 1 a name-distance matrix
                                              #   weighting coefficient
              }
    tr_geo = {'normalization': [],              # No normalization needed
              'metric': ald.geographical,         # Use the geographical distance
              'metric_params': {'units': 'km'},# Arguments given the
                                                #   distance function. Here,
                                                #   the unit to use
              'weighting': 1
             }

    processings = {1: tr_name, 2: tr_geo}

    print("Alignment started")
    align(alignset,           # The dataset to align
          targetset,          # The target dataset
          0.4,                # The maximal distance
                              #   threshold
          processings,         # The list of processings to
                              #   apply.
          dpath('demo1_results'))
                              # Filename of the output
                              #   result file
    # the ``align()`` function return two items
    # 0. the computed distance matrix
    # 1. a boolean, True if at least one alignment has been done, False
    #    otherwise
    print("Done, see the results in %s" % dpath('demo1_results'))

def demo_2():
    targetset = parsefile(dpath('FR.txt'), indexes=[0, 1, (4, 5)],
                          formatopt={1:lambda x:x.decode('utf-8')})
    alignset = parsefile(dpath('frenchbnf'), indexes=[0, 2, (14, 12)],
                         formatopt={2:lambda x:x.decode('utf-8')}, nbmax=30000)

    print("Finding neighbours")
    neighbours = findneighbours(alignset, targetset, indexes=(2, 2),
                               mode='minibatch')

    # Let's define the processings to apply on the location's name
    tr_name = {'normalization': [aln.simplify], # Simply all the names (remove
                                              #   punctuation, lower case, etc)
               'metric': ald.levenshtein,     # Use the levenshtein distance
               'weighting': 1                 # Use 1 a name-distance matrix
                                              #   weighting coefficient
              }

    processings = {1: tr_name}
    print("Start computation")
    for ind, (alignid, targetid) in enumerate(neighbours):
        print('%3d' % ind, len(alignid), 'x', len(targetid))
        _, matched = subalign(alignset,   # The dataset to align
                              targetset,  # The target dataset
                              alignid,
                              targetid,
                              0.3,
                              processings)
        write_results(matched, alignset, targetset, dpath('demo2_results'))
    print("Done, see the results in %s" % dpath('demo2_results'))

def demo_3():
    print("Parsing files")
    alignset = parserql(host='http://demo.cubicweb.org/elections/',
                        rql='Any E, N WHERE X is Commune, X eid E, X label N')
    targetset = parsefile(dpath('FR.txt'), indexes=[0, 1])
    print('%s×%s' % (len(alignset), len(targetset)))

    tr_name = {'normalization': [aln.simplify],
               'metric': 'levenshtein'
              }

    print("Alignment started")
    results = alignall(alignset, targetset, 0.75, processings={1: tr_name},
                       indexes=(1,1), mode='minhashing', kwordsgram=1, siglen=200,
                       uniq=True)
    dicresults = dict([(a, b) for (a, b) in results])

    print("Done, writing output")

    with open(dpath('demo3_results'), 'w') as fout:
        for line in alignset:
            sent = u'http://demo.cubicweb.org/elections/commune/%s;'\
                   u'http://www.geonames.org/%s\n' \
                   % (line[0], dicresults.get(line[0], 'not_found'))
            fout.write(sent.encode('utf-8'))

    print("See the results in %s" % dpath('demo3_results'))

if __name__ == '__main__':
    import sys
    from time import time
    runall = (len(sys.argv) == 1)

    t = time()
    if runall or '0' in sys.argv:
        print("Running demo_0")
        demo_0()

    if runall or '1' in sys.argv:
        print("Running demo_1")
        demo_1()

    if runall or '2' in sys.argv:
        print("Running demo_2")
        ## Same as demo_1, but in a more efficient way, using a method to find
        ## neighbours
        demo_2()

    if runall or '3' in sys.argv:
        print("Running demo_3")
        demo_3()

    print("Demo terminated")
    print("Took %d min" % ((time() - t)/60.))
