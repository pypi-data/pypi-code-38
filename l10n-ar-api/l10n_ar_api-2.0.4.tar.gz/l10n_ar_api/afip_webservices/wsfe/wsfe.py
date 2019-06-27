# -*- coding: utf-8 -*-
# Segun RG 2485 – Proyecto FE v2.8 - 12/09/2016

from zeep import Client

from .error import AfipError
from l10n_ar_api.afip_webservices import config
from .invoice import ElectronicInvoiceValidator


class WsfeInvoiceDetails(object):
    """ 
    Se encarga de asignar los detalles de una invoice en
    los factories de WSFE.
    
    :param client: Cliente / Webservice.
    :param invoice: Objeto ElectronicInvoice para tomar los detalles.
    :param last_invoice_number: Ultimo numero de comprobante.
    """
    
    def __init__(self, client, invoice, last_invoice_number):
        self.client = client
        self.invoice = invoice
        self.last_invoice_number = last_invoice_number
        self.detail = None

    def get_details(self):
        """ Devuelve los detalles completos para esa factura """
        
        self._set_details()

        return self.detail
        
    def _set_details(self):
        """ Completa los detalles a enviar segun los datos del documento """

        self.detail = self._get_detail()
        self.detail.Concepto = self.invoice.concept
        self.detail.DocTipo = self.invoice.customer_document_type
        self.detail.DocNro = self.invoice.customer_document_number
        self.detail.CbteDesde = self.last_invoice_number+1
        self.detail.CbteHasta = self.last_invoice_number+1
        self.detail.CbteFch = self.invoice.document_date
        self.detail.ImpTotal = self.invoice.get_total_amount()
        self.detail.ImpTotConc = self.invoice.untaxed_amount
        self.detail.ImpNeto = self.invoice.taxed_amount
        self.detail.ImpOpEx = self.invoice.exempt_amount
        self.detail.ImpIVA = self.invoice.get_total_iva()
        self.detail.ImpTrib = self.invoice.get_total_tributes()
        if self.invoice.concept not in [2, 3]:
            self.detail.FchServDesde = ''
            self.detail.FchServHasta = ''
            self.detail.FchVtoPago = ''
        else:
            self.detail.FchServDesde = self.invoice.service_from
            self.detail.FchServHasta = self.invoice.service_to
            self.detail.FchVtoPago = self.invoice.payment_due_date
        self.detail.MonId = self.invoice.mon_id
        self.detail.MonCotiz = round(self.invoice.mon_cotiz, 6)
        self._set_iva()
        self._set_tributes()

    def _serialize_tribute(self, tribute):
        return self._get_tribute()(
            Id=tribute.document_code,
            BaseImp=tribute.taxable_base,
            Alic=tribute.aliquot,
            Importe=tribute.amount
        )

    def _set_tributes(self):
        """ Agrega al detalle el array de tributos del documento """

        if self.invoice.array_tributes:
            self.detail.Tributos = self._get_tribute_array()([
                self._serialize_tribute(tribute) for tribute in self.invoice.array_tributes
            ])

    def _serialize_iva(self, iva):
        return self._get_iva()(
            Id=iva.document_code,
            BaseImp=iva.taxable_base,
            Importe=iva.amount
        )

    def _set_iva(self):
        """ Agrega al detalle el array de iva del documento """

        if self.invoice.array_iva:
            self.detail.Iva = self._get_iva_array()([
                self._serialize_iva(iva) for iva in self.invoice.array_iva
            ])

    def _get_detail(self):
        return self.client.type_factory('ns0').FECAEDetRequest()

    def _get_iva(self):
        return self.client.get_type('ns0:AlicIva')

    def _get_iva_array(self):
        return self.client.get_type('ns0:ArrayOfAlicIva')

    def _get_tribute(self):
        return self.client.get_type('ns0:Tributo')

    def _get_tribute_array(self):
        return self.client.get_type('ns0:ArrayOfTributo')


class Wsfe(object):
    """
    Factura electronica.
    
    :param access_token: AccessToken - Token de acceso
    :param cuit: Cuit de la empresa
    :param homologation: Homologacion si es True
    :param url: Url de servicios para Wsfe
    """
        
    def __init__(self, access_token, cuit, homologation=True, url=None):
        if not url:
            self.url = config.service_urls.get('wsfev1_homologation') if homologation\
                else config.service_urls.get('wsfev1_production')
        else:
            self.url = url
        
        self.accessToken = access_token
        self.cuit = cuit
        self.auth_request = self._create_auth_request()

    def check_webservice_status(self):
        """ Consulta el estado de los webservices de AFIP."""
        
        res = Client(self.url).service.FEDummy()

        if hasattr(res, 'Errors'):
            raise AfipError.parse_error(res)
        if res.AppServer != 'OK':
            raise Exception('El servidor de aplicaciones no se encuentra disponible. Intente mas tarde.')
        if res.DbServer != 'OK':
            raise Exception('El servidor de base de datos no se encuentra disponible. Intente mas tarde.')
        if res.AuthServer != 'OK':
            raise Exception('El servidor de auntenticacion no se encuentra disponible. Intente mas tarde.')

    def get_cae(self, invoices, pos):
        """
        :param invoices: Conjunto de Objetos ElectronicInvoice, documentos a enviar a AFIP.
        :param pos: Numero de punto de venta.
        :returns str: Respuesta de AFIP sobre la validacion del documento.
        """
        
        self._validate_invoices(invoices)      
        FECAERequest = self._set_FECAERequest(invoices, pos)
        # FECAESolicitar(Auth: ns0:FEAuthRequest, FeCAEReq: ns0:FECAERequest) ->
        # FECAESolicitarResult: ns0:FECAEResponse
        return Client(self.url).service.FECAESolicitar(
            Auth=self.auth_request,
            FeCAEReq=FECAERequest
        ), FECAERequest

    def show_error(self, response):
        if response.Errors:
            raise AfipError.parse_error(response)

    def get_last_number(self, pos_number, document_type_number):
        """
        :param pos_number: Numero de punto de venta
        :param document_type_number: Numero del tipo de documento segun AFIP a consultar 
        :return: Numero de ultimo comprobante autorizado para ese tipo
        """

        # FECompUltimoAutorizado(Auth: ns0:FEAuthRequest, PtoVta: xsd:int, CbteTipo: xsd:int) ->
        # FECompUltimoAutorizadoResult: ns0:FERecuperaLastCbteResponse

        last_number_response = Client(self.url).service.FECompUltimoAutorizado(
            Auth=self.auth_request,
            PtoVta=pos_number,
            CbteTipo=document_type_number,
        )
        if last_number_response.Errors:
            raise AfipError().parse_error(last_number_response)

        return last_number_response.CbteNro
        
    def _validate_invoices(self, invoices):
        """
        Valida que los campos de la factura electronica sean validos
        
        :param invoices: Lista de Objetos Invoice, documentos a validar.
        """
        
        invoiceValidator = ElectronicInvoiceValidator()
        for invoice in invoices:
            invoiceValidator.validate_invoice(invoice)  
        
    def _get_header(self):
        return Client(self.url).get_type('ns0:FECAECabRequest')

    def _get_cae_request(self):
        return Client(self.url).get_type('ns0:FECAERequest')

    def _get_array_cae_request(self):
        return Client(self.url).get_type('ns0:ArrayOfFECAEDetRequest')

    def _get_document_type(self, invoices):
        document_types = set([invoice.document_code for invoice in invoices])
        if len(document_types) > 1:    
            raise AttributeError("Los documentos a enviar deben ser del mismo tipo")
        
        return next(iter(document_types))
   
    def _set_FECAERequest(self, invoices, pos):
        """
        :param invoices: Conjunto de objetos ElectronicInvoice.
        :param pos: Numero de punto de venta.
        :returns: FECAERequest / Envio de documentos para recibir el CAE.
        """
        
        header = self._set_header(invoices, pos)
        array_cae_request = self._get_array_cae_request()

        details = []
        last_invoice = self.get_last_number(header.PtoVta, header.CbteTipo)
        
        for invoice in invoices:
            details.append(WsfeInvoiceDetails(Client(self.url), invoice, last_invoice).get_details())
            last_invoice += 1

        cae_request = self._get_cae_request()

        # ns0:FECAERequest(FeCabReq: ns0:FECAECabRequest, FeDetReq: ns0:ArrayOfFECAEDetRequest)
        FECAERequest = cae_request(
            FeCabReq=header,
            FeDetReq=array_cae_request(details)
        )

        return FECAERequest

    def _set_header(self, invoices, pos):
        """
        :param invoices: Conjunto de Objetos ElectronicInvoice.
        :param pos: Numero de punto de venta.
        :returns: FeCabReq / cabecera de envio de documentos completo.
        """
        
        header_request = self._get_header()
        # ns0:FECAECabRequest(CantReg: xsd:int, PtoVta: xsd:int, CbteTipo: xsd:int)
        header = header_request(
            CantReg=len(invoices),
            PtoVta=pos,
            CbteTipo=self._get_document_type(invoices)
        )

        return header
        
    def _create_auth_request(self):
        """ Setea el FEAuthRequest, necesario para utilizar el resto de los metodos """

        FEAuthRequest = Client(self.url).get_type('ns0:FEAuthRequest')
        # ns0:FEAuthRequest(Token: xsd:string, Sign: xsd:string, Cuit: xsd:long)
        auth_request = FEAuthRequest(
            Token=self.accessToken.token,
            Sign=self.accessToken.sign,
            Cuit=self.cuit
        )
        return auth_request
