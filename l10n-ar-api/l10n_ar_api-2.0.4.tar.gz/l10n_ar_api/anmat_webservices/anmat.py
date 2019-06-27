# -*- coding: utf-8 -*-
# Segun RG 2485 – Proyecto FE v2.8 - 12/09/2016
import sys
sys.path.append("..")
from zeep import Client
from zeep.plugins import HistoryPlugin
from zeep.wsse.username import UsernameToken
from l10n_ar_api.anmat_webservices import config
from lxml import etree
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


import traceback
LOCATION = {
    'location_homologation': 'https://localhost:443/trazaenprodmed.WebService',
    'location_production': 'https://localhost:443/trazaprodmed.WebService',
}


class Anmat(object):
    """ Conexion con WS de ANMAT"""

    def __init__(self, login_data, prueba=False, url=None):
        if url:
            self.url = url
        else:
            self.url = config.service_urls.get('ws_anmat_homologation') if prueba else config.service_urls.get('ws_anmat_production')

        self.usuario = login_data.get('usuario')
        self.password = login_data.get('password')
        self.client = None
        self.history = HistoryPlugin()
        self.CodigoTransaccion = self.Excepcion = self.Errores = self.Resultado = self.Traceback = ""
        self.conectar(wsdl=self.url, prueba=prueba)

    def conectar(self, wsdl=None, prueba=False):
        """Conectar cliente soap del web service"""
        try:
            # Analizar transporte y servidor proxy:
            self.wsdl = self.url
            if not wsdl:
                wsdl = self.wsdl
            # Agregar sufijo para descargar descripción del servicio ?WSDL o ?wsdl
            if not wsdl.endswith(self.wsdl[-5:]) and wsdl.startswith("http"):
                wsdl += self.wsdl[-5:]
            self.client = Client(
                self.url,
                wsse=UsernameToken(
                    'testwservice',
                    'testwservicepsw'
                ),
                plugins=[self.history]
            )
            url = urlparse(wsdl)
            location = LOCATION.get('location_homologation').replace("localhost", url.hostname) if prueba else\
                LOCATION.get('location_production').replace("localhost", url.hostname)
            for service in self.client.wsdl.services.values():
                for port in service.ports.values():
                    port.binding_options['address'] = location
            self.client.service._binding_options['address'] = location
            return True
        except:
            info = sys.exc_info()
            ex = traceback.format_exception(info[0], info[1], info[2])
            self.Traceback = ''.join(ex)
            try:
                self.Excepcion = traceback.format_exception_only(info[0], info[1])[0]
            except:
                self.Excepcion = "No disponible"
            raise

    def _analizar_errores(self, res):
        """Comprueba y extrae errores si existen en la respuesta XML"""

        if res.errores:
            self.Errores = "%s: %s" % (res.errores[0]['c_error'], res.errores[0]['d_error'])
        self.Resultado = res.resultado

    def informar_producto(self, datos_de_envio):
        """
        :param datos_de_envio: lista de diccionario con valores de la transaccion
        """
        res = self.client.service.informarProducto(
            transacciones=datos_de_envio, usuario=self.usuario, password=self.password
        )
        self.CodigoTransaccion = res.codigoTransaccion
        self._analizar_errores(res)
        return True

    def cancelar_transaccion(self, codigo_transaccion):
        """
        parameter: codigo_transaccion {
            codigo de transaccion a cancelar
        }
        """
        res = self.client.service.sendCancelacTransacc(
            transaccion=codigo_transaccion, usuario=self.usuario, password=self.password
        )
        self.CodigoTransaccion = res.codigoTransaccion
        self._analizar_errores(res)
        return True

    def cancelar_transaccion_parcial(self, codigo_transaccion, producto_data):
        """
        :param codigo_transaccion codigo de transaccion a cancelar
        :param producto_data diccionario de gtin y serie de producto a cancalar
        """
        res = self.client.service.sendCancelacTransaccParcial(
            transaccion=codigo_transaccion, usuario=self.usuario,
            password=self.password, gtin=producto_data.get('gtin'), serie=producto_data.get('nro_serie')
        )
        self.CodigoTransaccion = res.codigoTransaccion
        self._analizar_errores(res)
        return True

    def get_xml_request(self):
        try:
            return etree.tostring(self.history.last_sent["envelope"], encoding="unicode", pretty_print=True)
        except (IndexError, TypeError):
            pass

    def get_xml_response(self):
        try:
            return etree.tostring(self.history.last_received["envelope"], encoding="unicode", pretty_print=True)
        except (IndexError, TypeError):
            pass
