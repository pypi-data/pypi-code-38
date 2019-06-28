import requests
import xml.etree.ElementTree as et
import xmltodict
import pandas as pd
import json
from zeep import Client
import operator

class SomToday:

    def __init__(self, username, password, environment, base_url=None):
        self.environment = environment
        self.username = username
        self.password = password
        self.base_url = 'https://{}-oop.somtoday.nl/services/umService?wsdl'.format(self.environment) if base_url is None else base_url


    def get_metadata(self):
        """
        This method gets the wsdl from the specified environment
        :return: returns all names of the available methods as dict keys, with the params as dict values
        """
        client = Client('https://{}-oop.somtoday.nl/services/umService?wsdl'.format(self.environment))
        methods = {}
        # get each operation signature
        for service in client.wsdl.services.values():
            print("service:", service.name)
            for port in service.ports.values():
                operations = sorted(
                    port.binding._operations.values(),
                    key=operator.attrgetter('name'))

                for operation in operations:
                    methods[operation.name] = [operation.input.signature()]

        return methods


    def get_data(self, dataset_name: str, params: dict):
        """
        This method is used to communicate with SomToday
        :param dataset_name: the name of the connector that you want to call
        :param params: parameters to the request. Different connectors allow different parameters. All are optional
        :return: df with response content
        """
        raw_body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://services.mijnsom.nl">
                   <soapenv:Header/>
                   <soapenv:Body>
                      <ser:{dataset_name}>
                      </ser:{dataset_name}>
                   </soapenv:Body>
                </soapenv:Envelope>""".format(dataset_name=dataset_name)
        root = et.fromstring(raw_body)
        body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        dataset_body = body.find('{http://services.mijnsom.nl}' + dataset_name)

        # Add subelements to body
        et.SubElement(dataset_body, 'brinNr')
        et.SubElement(dataset_body, 'username')
        et.SubElement(dataset_body, 'password')

        # Set value to subelements
        dataset_body.find('brinNr').text = params['brin']
        dataset_body.find('username').text = self.username
        dataset_body.find('password').text = self.password

        if dataset_name != 'getInrichtingVestigingen' and 'schooljaar' in params:
            et.SubElement(dataset_body, 'schooljaar')
            dataset_body.find('schooljaar').text = params['schooljaar']

        if dataset_name in ['getDataDebiteuren', 'getDataLeerlingen', 'getDataMedewerkers', 'getDataVerzorgers'] and 'vestiging_afkorting' in params:
            et.SubElement(dataset_body, 'vestigingAfkorting')
            dataset_body.find('vestigingAfkorting').text = params['vestiging_afkorting']

        if dataset_name in ['getInrichtingLesgroepen', 'getInrichtingOpleidingen', 'getInrichtingStamgroepen', 'getInrichtingVakken'] and 'vestigingID' in params:
            et.SubElement(dataset_body, 'vestigingID')
            dataset_body.find('vestigingID').text = params['vestigingID']

        if dataset_name == 'getInrichtingOpleidingVakken':
            if 'opleidingID' in params:
                et.SubElement(dataset_body, 'opleidingID')
                dataset_body.find('opleidingID').text = params['opleidingID']
            if 'leerjaar' in params:
                et.SubElement(dataset_body, 'leerjaar')
                dataset_body.find('leerjaar').text = params['leerjaar']

        et.dump(root)
        response = requests.post(self.base_url, data=et.tostring(root))
        if response.status_code == 200:
            dict_data = xmltodict.parse(response.text)
            json_data = json.dumps(dict_data)
            item_dict = json.loads(json_data)['soap:Envelope']['soap:Body']['ns2:{dataset_name}Response'.format(dataset_name=dataset_name)]
            if 'return' in item_dict:
                item_dict = item_dict['return']
            else:
                print("empty response")
                return pd.DataFrame()
            df = pd.DataFrame(item_dict)

            return df
        else:
            raise Exception(response.text)


    def write_data(self, dataset_name: str, params: dict):
        """
        This method is used to communicate with SomToday
        :param dataset_name: the name of the connector that you want to call
        :param params: parameters to the request. Different connectors allow different parameters. All are optional
        :return:
        """
        # TODO: This is not implemented fully yet. WSDL can be found at https://pantar-oop.somtoday.nl/services/umService?wsdl
        return "Nog niet geïmplementeerd. Dient slechts ter voorbeeld"

        # raw_body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://services.mijnsom.nl">
        #            <soapenv:Header/>
        #            <soapenv:Body>
        #               <ser:{dataset_name}>
        #               </ser:{dataset_name}>
        #            </soapenv:Body>
        #         </soapenv:Envelope>""".format(dataset_name=dataset_name)
        # root = et.fromstring(raw_body)
        # body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        # dataset_body = body.find('{http://services.mijnsom.nl}' + dataset_name)
        #
        # # Add subelements to body
        # et.SubElement(dataset_body, 'brinNr')
        # et.SubElement(dataset_body, 'username')
        # et.SubElement(dataset_body, 'password')
        #
        # # Set value to subelements
        # dataset_body.find('brinNr').text = params['brin']
        # dataset_body.find('username').text = self.username
        # dataset_body.find('password').text = self.password
        #
        # if dataset_name == 'writeDataLeerlingen':
        #     et.SubElement(dataset_body, 'leerlingen')
        # elif dataset_name == 'writeDataMedewerkers':
        #     et.SubElement(dataset_body, 'medewerkers')
        # elif dataset_name == 'writeDataVerzorgers':
        #     et.SubElement(dataset_body, 'verzorgers')
        #
        # et.dump(root)



    # TODO: laten staan ter voorbeeld.
    def get_all_data(self, brins: [], schooljaar: str):
        return "Nog niet geïmplementeerd. Dient slechts ter voorbeeld"
        # methods = self.get_metadata().keys()
        # for method in methods:
        #     if 'get' in method:
        #         output = pd.DataFrame()
        #         for brin in brins:
        #             data = self.get_data(dataset_name=method, params={
        #                 "schooljaar": schooljaar,
        #                 "brin": brin
        #             })
        #             output = pd.concat([output, data])