import json
import requests


class Request:
    TERRAVISIE = "https://terravisie.sobolt.com"

    api_key = None
    service = None
    version = 1
    crs     = { "type":       "EPSG",
                "properties": { "code": 4326,
                                "coordinate_order": [1, 0]
              } }


    def __init__(self, api_key, service = None, version = 1):
        if service is None:
            service = Request.TERRAVISIE

        if api_key is None:
            raise ValueError("api_key == None but an API key must be supplied")

        self.api_key = api_key
        self.service = service
        self.version = version


    # The method do_request performs an HTTP request to Sobolt's servers, submitting the
    # image to be analysed. The return value is either a dictionary of the
    # parsed JSON values, or the raw JSON text if the parse parameter was set to False.
    # In, img_url:  A url pointing the image to be downloaded and analyzed
    # In, img_bbox: A prepared WKT Polygon string with the image's bounding box
    # In, tpis: A list of dictionary, where each dictionary describes a TPI and has
    #           the keys: (1) 'bounding_box' with a value of WKT Polygon string;
    #                     (2) 'id' being an int
    #                     (3) 'point' with a WKT Point string
    #           The tpis parameter is optional and is ignored when it evaluates
    #           to False or is None.
    # In, parse:  (Optional) Whether the response must be parsed or not
    # Out: JSON text
    # Exception: Might raise exceptions for incorrect JSON or failed HTTP requests
    def do_request(self, img_url, img_bbox, tpis=None, parse=True):
        data = { "api_key": self.api_key,
                 "version": self.version,
                 "crs":     self.crs,
                 "image":   { "url": img_url,
                              "bounding_box": img_bbox
                            }
               }

        if tpis:
            data['tpis'] = tpis

        data = json.dumps(data)
        json_response = self.do_request_get_response(data)

        if json_response.status_code == 200:
            if parse:
                return json_response.json()
            else:
                return json_response.text
        else:
            json_response.raise_for_status()


    # The method do_request_get_response performs an HTTP request to Sobolt's servers,
    # submitting raw json, without doing any further processing.
    # The return value is the response object as the requests module returns.
    def do_request_get_response(self, data):
        headers = { "Content-Type": "application/json" }
        json_response = requests.post(self.service,
                                      data=data,
                                      headers=headers)

        json_response.close()
        return json_response
