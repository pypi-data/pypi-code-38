# coding=utf-8

import requests
import hashlib
import xml.etree.cElementTree as et
from dateutil.relativedelta import relativedelta
from . import config
from os.path import abspath


def create_file(path, date):
    root = et.Element("DESCARGA-PADRON")
    et.SubElement(root, 'fechaDesde').text = date.replace(day=1).strftime('%Y%m%d')
    et.SubElement(root, 'fechaHasta').text = (date.replace(day=1) + relativedelta(months=1, days=-1)).strftime('%Y%m%d')
    tree = et.ElementTree(root)
    tree.write(path)


def get_md5(path):
    padron_request_file = open(path, 'r')
    content = padron_request_file.read()
    return hashlib.md5(content.encode()).hexdigest()


class IIBBPadron(object):

    """
    Descarga de padrón según especificaciones
    http://www.arba.gov.ar/Domicilio_Electronico/VerPDF.asp?param=ES
    """
    def __init__(self, user, password, homologation=False):
        self.user = user
        self.password = password
        self.url = config.authorization_urls['homologation'] if homologation else \
            config.authorization_urls['production']

    def get_padron(self, date, request_path='/tmp/padron_request.xml', padron_path='/tmp/padron.zip'):
        """
        Descarga el padron otorgado por ARBA
        :param date: Fecha de la cual se desea obtener el padron
        :param request_path: Ruta donde se creará el archivo de request.
        :param padron_path: Ruta donde se descargará el padrón.
        """
        
        create_file(request_path, date)
        filename = get_md5(request_path)
        
        with open(request_path, 'r') as fileaenviar, open(padron_path, 'wb') as filearecibir:
            r = requests.post(
                self.url,
                data={'user': self.user, 'password': self.password},
                files={'file': ('DFEServicioDescargaPadron_'+filename+'.xml', fileaenviar, 'text/xml')},
            )
            filearecibir.write(r.content)

        return abspath(padron_path)
