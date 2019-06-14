import json
import os
import luigi
import requests
import time
import datetime
import logging
from luigi.contrib.esindex import CopyToIndex
from luigi.util import requires, inherits

logger = logging.getLogger(__name__)

GSICRAWLER_ENDPOINT = os.environ.get('GSICRAWLER_ENDPOINT',
                                     'http://crawler.social.cluster.gsi.dit.upm.es/api/v1')
SENPY_ENDPOINT = os.environ.get('SENPY_ENDPOINT',
                                'http://test.senpy.cluster.gsi.dit.upm.es/api/')
ES_HOST = os.environ.get('ES_HOST', 'localhost')
ES_PORT = int(os.environ.get('ES_PORT', '9200'))


class Senpy(luigi.Task):
    """
    Template task for analysing data with Senpy.
    """

    algorithm = luigi.Parameter(description='Algorithm to use for the analysis', default='default')
    senpy_host = luigi.Parameter(description='Senpy server', default=SENPY_ENDPOINT)
    fieldName = luigi.Parameter(description='Field in the document to use as nif:isString', default='schema:articleBody')
    lang = luigi.Parameter(description='Language of the text', default='en')
    senpy_timeout = luigi.FloatParameter(description='Time between requests', default=float(0.2), significant=False)

    @property
    def apiKey(self):
        "Senpy apiKey if required"
        return ''

    def run(self):
        """
        Run analysis task 
        """
        total = 0
        with self.input().open('r') as fobj:
            for line in fobj:
                total += 1
        self.set_progress_percentage(0)
        with self.input().open('r') as fobj:
            with self.output().open('w') as outfile:
                for ix, line in enumerate(fobj):
                    i = json.loads(line)
                    keep = {}
                    keep['@id'] = i['@id']
                    keep['_id'] = i['@id']
                    keep['@type'] = i['@type']
                    r = requests.post(self.senpy_host,
                                      data={'input': i[self.fieldName],
                                            'apiKey': self.apiKey,
                                            'algo': self.algorithm,
                                            'lang': self.lang})
                    if r.status_code != 200:
                        raise Exception('Error {} analysing: {}. Error [{}: {}'.format(r.status_code,
                                                                                       i[self.fieldName],
                                                                                       r.text))
                    resp = r.json()
                    logger.info('Sleeping for {} seconds'.format(self.senpy_timeout))
                    time.sleep(self.senpy_timeout)
                    logger.info(resp)
                    i.update(resp["entries"][0])
                    i.update(keep)
                    self.set_progress_percentage((100.0*ix)/total)
                    self.set_status_message("Done: %d. Last one: %s" % (ix, i))
                    outfile.write(json.dumps(i))
                    outfile.write('\n')

    def output(self):
        return luigi.LocalTarget('/tmp/soneti-senpy-{}'.format(self.task_id))


class CopyToFuseki(luigi.Task):
    """
    Template task for inserting a dataset into Fuseki.
    """

    @property
    def host(self):
        "Fuseki endpoint"
        return 'localhost'

    @property
    def port(self):
        "Fuseki endpoint port"
        return 3030

    @property
    def dataset(self):
        "Fuseki dataset"
        return 'default'

    def run(self):
        """
        Run indexing to Fuseki task 
        """
        f = []

        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:
                for i, line in enumerate(infile):
                    self.set_status_message("Lines read: %d" % i)
                    w = json.loads(line)
                    f.append(w)
                f = json.dumps(f)
                self.set_status_message("JSON created")
                r = requests.post('http://{fuseki}:{port}/{dataset}/data'.format(fuseki=self.fuseki_host,
                                                                                port=self.port, dataset = self.dataset),
                    headers={'Content-Type':'application/ld+json'},
                    data=f)
                self.set_status_message("Data sent to fuseki")
                outfile.write(f)



class GSICrawler(luigi.Task):
    """
    Template task for retrieving data with GSICrawler.
    """

    crawler_host = luigi.Parameter(description='GSICrawler endpoint', default=GSICRAWLER_ENDPOINT)
    source = luigi.Parameter(description='GSICrawler source')
    query = luigi.Parameter(description='query string. E.g. "terrorism", or "python programming"')
    number = luigi.IntParameter(description='number of documents to retrieve', default=10)
    taskoutput = luigi.ChoiceParameter(description='return the results in json format, or into an elasticsearch index',
                                       choices=['json', 'elasticsearch'], default='json')
    esendpoint = luigi.Parameter(description='Elasticsearch endpoint to store the resonts into', default="")
    index = luigi.Parameter(description='Elasticsearch index to use when storing in ES', default="")
    doctype = luigi.Parameter(description='Elasticsearch doc type', default="")

    max_wait = luigi.IntParameter(description='Maximum number of seconds to wait for the result', default=5*60)
    key = luigi.Parameter(description=('Identifier for the crawler tasks. Crawling tasks are not idempotent at the time,'
                                      'so an identifier is needed to change the parameters and force the task to run again.'),
                         default='default')
    crawl_timeout = luigi.IntParameter(description='Maximum time (in seconds) to wait for the task to complete before returning the Task information',
                                       significant=False,
                                       default=-1)
    crawl_wait = luigi.IntParameter(description='Time to wait (in seconds) between retries',
                                    significant=False,
                                    default=10)
    other = luigi.DictParameter(description='Other parameters to pass to the GSICrawler service', default={})

    def output(self):
        return luigi.LocalTarget('/tmp/soneti-crawler-{}'.format(self.task_id))
    
    def run(self):
        """
        Run analysis task 
        """
        params = {'query': self.query,
                  'number': self.number,
                  'output': self.taskoutput,
                  'esendpoint': self.esendpoint,
                  'index': self.index,
                  'timeout': self.crawl_timeout,
                  'doctype': self.doctype,
                  **self.other}
        url = '{}/scrapers/{}/'.format(self.crawler_host, self.source)
        r = requests.get(url, params=params)
        code = r.status_code
        response = r.json()

        if code > 202:
            raise Exception('Failed to crawl: {}'.format(r.text))

        task_id = response['task_id']
        attempts = 0
        logger.info(response)
        self.set_status_message('{}'.format(response))
        while code != 200:
            #self.set_status_message('Waiting for results ({} times). Last response: {}'.format(attempts,response))
            if attempts*self.crawl_wait/60.0 >= self.max_wait:
                raise Exception('Timed out waiting for task to finish: {}'.format(task_id))
            attempts += 1
            time.sleep(self.crawl_wait)
            url = self.crawler_host+'/tasks/'+task_id
            r = requests.get(url)

            code = r.status_code
            response = r.json()

        if 'results' not in response:
            raise Exception('Invalid output from the service: {}'.format(response))

        results = response['results']
        logger.info('{} got {} results'.format(self.source, len(results)))
        self.set_status_message("Number of results: %d" % len(results))
        with self.output().open('w') as outfile:
            for post in results:
                outfile.write(json.dumps(post))
                outfile.write('\n')


@inherits(GSICrawler)
class Twitter(luigi.WrapperTask):
    """
    GSICrawler scraper for Twitter.
    """
    querytype = luigi.ChoiceParameter(description='Use public search or timeline', choices=['timeline', 'search'], default='search')
    source = 'twitter'

    def requires(self):
        other = dict(self.other)
        other['querytype'] = self.querytype
        self.other = other
        t = self.clone(GSICrawler)
        return t

    def output(self):
        return self.input()


@inherits(GSICrawler)
class Facebook(luigi.WrapperTask):
    number = luigi.IntParameter(description='Number of results to show', default=100)
    source = 'facebook'

    def requires(self):
        other = dict(self.other)
        other['number'] = self.number
        self.other = other
        t = self.clone(GSICrawler)
        return t


class ElasticSearch(CopyToIndex):

    host = luigi.Parameter(default=ES_HOST, description='ElasticSearch endpoint')
    port = luigi.IntParameter(default=ES_PORT, description='ElasticSearch port')
    index = luigi.Parameter(description='ElasticSearch index', default='soneti')

    doc_type = luigi.Parameter(description='ElasticSearch doc type', default='default')

    def _docs(self):
        '''Add elasticsearch _ids based on the json-ld @id property, if _id is not given.'''
        # There might be a bug here in python 3.7 when there are no results from the _docs method.
        # This is due to the way the elasticsearch luigi module handles iterators, and
        # the change introduced in Python 3.7: https://www.python.org/dev/peps/pep-0479/
        for doc in super(ElasticSearch, self)._docs():
            if '_id' not in doc and '@id' in doc:
                doc['_id'] = doc['@id']
            yield doc


class SimpleMain(luigi.Task):

    stamp = luigi.IntParameter(time.time(), 'Timestamp for the task.')

    @property
    def id(self):
        return stamp(self.interval)

    def file(self):
        return '/tmp/{}-{}'.format(self.id, self.task_id)

    def output(self):
        return luigi.LocalTarget(self.file())

    def run(self):
        with self.output().open('w') as f:
            done = datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%S')
            f.write('DONE@{} - {}'.format(done, self.task_id))


def stamp(interval=60):
    seconds = datetime.datetime.today().timestamp()
    mod = seconds - (seconds % (60*interval))
    snap = datetime.datetime.fromtimestamp(mod)
    fmt = snap.strftime('%Y-%m-%d.%H-%M')
    return fmt
