import datetime
import json
import time
import pandas as pd
import requests
from pandas.io.json import json_normalize


class Elastic:

    def __init__(self, host):
        self.host = host

    def get_data(self, index):
        start = time.time()
        size = 10000

        #Get all indices with the given index from the function parameter. For each day a new index.
        indices = requests.get(url=self.host + '/' + index + '*/_settings').json()

        indexList = {}
        for line in indices:
            vDate = datetime.date(int(line[-10:-6]), int(line[-5:-3]), int(line[-2:]))
            indexList[str(vDate)] = line

        for key, value in sorted(indexList.items()):
            if key == str(time.strftime("%Y-%m-%d")):
                url = self.host + '/' + value + '/_search'

        # initial request
        params = {"size": size, "scroll": "10m"}
        response = requests.get(url=url, params=params).json()

        # next requests until finished
        scrollId = response['_scroll_id']
        total = response['hits']['total']
        initResponse = json_normalize(response['hits']['hits'])
        initResponse.drop(['_id', '_index', '_score', '_type'], axis=1, inplace=True)

        # start all the request to elastic based on the scroll_id and add to the initial response
        loopBoolean = True
        body = json.dumps({"scroll": "10m", "scroll_id": scrollId})
        url = self.host + '/_search/scroll'
        headers = {'Content-Type': 'application/json'}

        while loopBoolean and total > size:
            nextResponse = json_normalize(requests.post(url=url, data=body, headers=headers).json()["hits"]["hits"])
            nextResponse.drop(['_id', '_index', '_score', '_type'], axis=1, inplace=True)
            initResponse = pd.concat([initResponse, nextResponse], ignore_index=True)
            print("Ik heb ", len(nextResponse) ," fijne regeltjes opgehaald")
            if len(nextResponse) != size:
                loopBoolean = False

        end = time.time()
        print('Exporting from Elastic took', end - start)

        return initResponse


    def delete_index(self, index):
        return requests.delete(self.host + '/' + index).json()
