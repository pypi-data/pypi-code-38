# basic class for LIME CRM interactions, bases itself on REST API
import requests
import yaml

class LIME(object):
    def __init__(self,yamlfile):
        self.base_url = None
        self.header = None
        self.initialize(yamlfile)
    def initialize(self,fname):
        cfg = yaml.load(open(fname,'rb'))
        api_key=cfg['lime'].get("api_key","NONE")
        if api_key == "NONE": 
            raise Exception("api_key missing in configuration")
        self.header={'x-api-key': api_key}
        base_url=cfg['lime'].get("base_url","NONE")
        if base_url == "NONE": raise Exception("base_url missing in configuration file")
        self.base_url = base_url
    
    def getHotelList(self,fields=[], maxrange=1000):
        ''' returns a dictionary of hotels with {id:{prop_1:val_1, prop_2:val_2 ...}} 
            fields contains the field names in Lime that are included. No type enforcement is performed 
            pars:
                fields = list of fieldnames to be retrieved from lime
                maxrange (optional) = number of records to be retrieved; note that by construction, lime IDs are offset by 1000.
        '''
        export_data = {}
        for i in range(maxrange):
            r = requests.get("{url}/api/v1/limeobject/hotels/{hotel_id}/".format(url=self.base_url, hotel_id = i+1000), headers=self.header)
            if r.ok:
                data = r.json()
                key = int(data.get("propertynumber",i))
                values = {}
                for field in fields:
                    values[field] = data.get(field,"")
                export_data[key] = values
        return export_data
