# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
import time
from lxml import etree
from M2Crypto import BIO, SMIME
import sys


class AccessRequerimentToken(object):
    
    def __init__(self, service, tz=pytz.utc):
        self._service = service
        self._timezone = tz

    def _create_tra(self):
        """
        uniqueId: Entero de 32 bits sin signo que junto con generationTime identifica el
        requerimiento.
        
        generationTime: Momento en que fue generado el requerimiento. La tolerancia de aceptacion
        sera de hasta 24 horas previas al requerimiento de acceso
        
        expirationTime: Momento en el que expira la solicitud. La tolerancia de aceptacion sera de
        hasta 24 horas posteriores al requerimiento de acceso.  
        
        service: Identificacion del WSN para el cual se solicita el TA.
        
        :return: Ticket de Requerimiento de Acceso
        """
        
        ticket_request = etree.Element('loginTicketRequest')
        ticket_request.set('version', '1.0')
        header = etree.SubElement(ticket_request, 'header')

        # uniqueId
        uniqueid = etree.SubElement(header, 'uniqueId')
        # Traemos la fecha actual
        timestamp = int(time.mktime(datetime.now().timetuple()))
        uniqueid.text = str(timestamp)
        
        # generationTime
        # Generamos el token con media hora atrasada
        tsgen = datetime.fromtimestamp(timestamp-1800)
        tsgen = pytz.utc.localize(tsgen).astimezone(self.timezone)
        gentime = etree.SubElement(header, 'generationTime')
        gentime.text = tsgen.isoformat()    

        # expirationTime
        # El token vence 4.5 horas despues
        tsexp = datetime.fromtimestamp(timestamp+14400)
        tsexp = pytz.utc.localize(tsexp).astimezone(self.timezone)
        exptime = etree.SubElement(header, 'expirationTime')
        exptime.text = tsexp.isoformat()
        exptime.tail = None

        # service
        serv = etree.SubElement(ticket_request, 'service')
        serv.text = self.service

        return etree.tostring(ticket_request)

    def sign_tra(self, private_key, certificate):

        smime = SMIME.SMIME()
        ks = BIO.MemoryBuffer(private_key.encode('ascii'))
        cs = BIO.MemoryBuffer(certificate.encode('ascii'))
        bf = BIO.MemoryBuffer(self._create_tra().decode('ascii').encode('ascii'))
        out = BIO.MemoryBuffer()

        try:
            smime.load_key_bio(ks, cs)
        except Exception:
            raise Exception('Error en el formato del certificado o clave privada')

        sbf = smime.sign(bf)
        smime.write(out, sbf)

        head, body, end = out.read().split(b'\n\n')
        return body
    
    @property
    def service(self):
        return self._service

    @property
    def timezone(self):
        return self._timezone


class AccessToken(object):
    
    """ Ejemplo de token:
    
    <?xml version="1.0" encoding="UTF8"?>
    <loginTicketResponse version="1.0">
    <header>
        <source>cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239</source>
        <destination>cn=srv1,ou=facturacion,o=empresa s.a.,c=ar,serialNumber=CUIT 30123456789</destination>
        <uniqueId>383953094</uniqueId>
        <generationTime>20011231T12:00:0203:00</generationTime>
        <expirationTime>20020101T00:00:0203:00</expirationTime>
    </header>
    <credentials>
        <token>cES0SSuWIIPlfe5/dLtb0Qeg2jQuvYuuSEDOrz+w2EnAQiEeS86gzYf7ehiU3UaYit5FRb9z/3zq</token>
        <sign>a6QSSZBgLf0TTcktSNteeSg3qXsMVjo/F5py/Gtw7xucTrUWbsrVCdIoGE8Cm1bixpuVPlr58k6n</sign>
    </credentials>
    </loginTicketResponse>
    """
    
    def __init__(self):
        # Header
        self.source = None
        self.destination = None
        self.uniqueId = None
        self.generation_time = None
        self.expiration_time = None

        # Credentials
        self.token = None
        self.sign = None
        
    def create_token_from_login(self, login_fault):
        """
        Asigna los atributos al token desde el login
        :param login_fault: XML con el login autorizado 
        """

        if sys.version_info[0] >= 3:
            login_fault_tree = etree.fromstring(login_fault.encode('ascii'))
        else:
            login_fault_tree = etree.fromstring(str(login_fault))

        try:
            
            self.source = login_fault_tree.find('header/source').text
            self.destination = login_fault_tree.find('header/destination').text
            self.generation_time = login_fault_tree.find('header/generationTime').text
            self.expiration_time = login_fault_tree.find('header/expirationTime').text
            
            self.token = login_fault_tree.find('credentials/token').text
            self.sign = login_fault_tree.find('credentials/sign').text
        
        except AttributeError:
            raise AttributeError("Error al generar el token de acceso")
