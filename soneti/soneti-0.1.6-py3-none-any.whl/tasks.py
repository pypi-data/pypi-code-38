name = "soneti_tasks"
import json
import luigi
import requests
import time

class SenpyAnalysis(luigi.Task):
    """
    Template task for analysing data with Senpy.
    """

    @property
    def host(self):
        "Senpy endpoint"
        return 'http://test.senpy.cluster.gsi.dit.upm.es/api/'

    @property
    def algorithm(self):
        "Senpy algorithm"
        return 'sentiment-tass'

    @property
    def fieldName(self):
        "json fieldName to analyse"
        return 'schema:articleBody'

    @property
    def apiKey(self):
        "Senpy apiKey if required"
        return ''

    @property
    def lang(self):
        "Senpy lang if required"
        return 'en'

    @property
    def timeout(self):
        "Time between requests"
        return 1
    
    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as fobj:
            with self.output().open('w') as outfile:
                fobj = json.load(fobj)
                for i in fobj:
                    b = {}
                    b['@id'] = i['@id']
                    b['_id'] = i['@id']
                    b['@type'] = i['@type']
                    r = requests.post(self.host,
                                      data={'input': i[self.fieldName],
                                            'apiKey': self.apiKey,
                                            'algo': self.algorithm,
                                            'lang': self.lang})
                    time.sleep(self.timeout)
                    print(r.json())
                    i.update(r.json()["entries"][0])
                    i.update(b)
                    outfile.write(json.dumps(i))
                    outfile.write('\n')


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
                r = requests.put('http://{fuseki}:{port}/{dataset}/data'.format(fuseki=self.host,
                                                                                port=self.port, dataset = self.dataset),
                    headers={'Content-Type':'application/ld+json'},
                    data=f)
                self.set_status_message("Data sent to fuseki")
                outfile.write(f)


class GSICrawlerScraper(luigi.Task):
    """
    Template task for retrieving data with GSICrawler.
    """

    host = luigi.Parameter(description='GSICrawler endpoint', default='http://crawler.social.cluster.gsi.dit.upm.es/api/v1')
    source = luigi.Parameter(description='GSICrawler source', default='twitter')
    query = luigi.Parameter(description='query string. E.g. "terrorism", or "python programming"', default="gsiupm")
    number = luigi.IntParameter(description='number of documents to retrieve', default=10)
    taskoutput = luigi.ChoiceParameter(description='return the results in json format, or into an elasticsearch index',
                                       choices=['json', 'elasticsearch'], default='json')
    esendpoint = luigi.Parameter(description='Elasticsearch endpoint to store the resonts into')
    index = luigi.Parameter(description='Elasticsearch index to use when storing in ES', default=None)
    doctype = luigi.Parameter(description='Elasticsearch doc type', default=None)

    max_wait = luigi.IntParameter(description='Maximum number of minutes to wait for the result', default=5)
    other = luigi.DictParameter(description='Other parameters to pass to the GSICrawler service')

    
    def run(self):
        """
        Run analysis task 
        """
        params = {'query': self.query,
                  'number': self.number,
                  'output': self.taskoutput,
                  'sendpoint': self.esendpoint,
                  'index': self.index,
                  'doctype': self.doctype,
                  'host': self.host,
                  'source': self.source,
                  'querytype': self.querytype,
                  **self.other}
        url = '{host}/scrapers/{source}/'.format(self.host, self.source)
        print(url)
        r = requests.get(url, params=params)
        code = r.status_code
        result = r.json()

        if code > 200:
            raise Exception('Failed to crawl: {}'.format(r.data))

        while code != 200:
            if self.max_wait <= 0:
                raise Exception('Timed out waiting for task to finish: {}'.format(task_id))
            self.max_wait -= 1
            time.sleep(60)
            url = self.host+'/tasks/'+result['task_id']
            r = requests.get(url)

            code = r.code
            result = r.json()
            print(result)

        if 'results' not in result:
            raise Exception('Invalid output from the service: {}'.format(result))

        with self.output().open('w') as outfile:
            outfile.write(result["results"])
