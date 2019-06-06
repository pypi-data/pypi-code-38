import argparse
from collections import defaultdict
import logging

import requests
from pysolr import Solr
from tqdm import tqdm

logger = logging.getLogger(__name__)

class CreateWordLists(object):
    def __init__(self,solr_url):
        self.solr = Solr(solr_url)


    def createWordListsPerYear(self,start,end,out_folder="/var/tmp"):
        for start in tqdm(range(start, end)):
            logger.debug("starting year:", start)
            words = defaultdict(int)
            end = start
            qs = self.solr.url + '/tvrh?fl=id&rows=10000000&q=date:[%s-01-01T00:00:00Z TO %s-12-31T23:59:00Z]&tv=true&tv.fl=nounphrase_exact&tv.tf=true' % (start, end)

            res = requests.get(qs).json()
            tvs = res["termVectors"]
            cnt = 0
            for tv_i in range(0, len(tvs), 2):
                doc = tvs[tv_i]
                cnt += 1
                if len(tvs[tv_i + 1]) < 4:
                    continue  # no terms
                vals = tvs[tv_i + 1][3]  # gives the list
                for v_i in range(0, len(vals), 2):
                    phr = vals[v_i]
                    num = vals[v_i + 1][1]

                    words[phr] += num
            logger.debug("writing year: %s (%s)" % (start, cnt))
            with open("/var/tmp/%s.words.txt" % start, "w", encoding="utf-8") as out:
                for k, v in words.items():
                    out.write("%s\t%s\n" % (k, v))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()


    solr_url = "http://%s:%s@dw2.mpiwg-berlin.mpg.de:38983/solr/abstracts"

    parser.add_argument('user',  type=str)
    parser.add_argument('password',  type=str)
    args = parser.parse_args()
    solr_url = solr_url%(args.user,args.password)
    cw = CreateWordLists(solr_url)
    cw.createWordListsPerYear(1930,1940)