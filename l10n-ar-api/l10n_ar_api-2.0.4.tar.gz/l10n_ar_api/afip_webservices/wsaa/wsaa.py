from zeep import Client
from requests import Session
from zeep.transports import Transport

from l10n_ar_api.afip_webservices import config


class Wsaa(object):

    def __init__(self, homologation=True, url=None):
        
        if not url:
            self.url = config.authorization_urls.get('homologation') if homologation\
                else config.authorization_urls.get('production')
        else:
            self.url = url

    def login(self, tra):
        """
        :param tra: TRA que se usara para el logeo
        :return: XML con el login autorizado
        """
        
        try:
            session = Session()
            session.verify = False
            transport = Transport(session=session)
            login_fault = Client(self.url, transport=transport).service.loginCms(tra)
        except Exception as e:
            raise Exception("Error al autenticarse\n{}".format(e))
        
        return login_fault
