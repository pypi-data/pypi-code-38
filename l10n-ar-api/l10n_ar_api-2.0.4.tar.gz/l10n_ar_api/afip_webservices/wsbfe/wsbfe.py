# -*- coding: utf-8 -*-
# Segun manual para el desarrollador version 28/12/2018
from l10n_ar_api.afip_webservices import config
from zeep import Client
from .error import AfipError
from .invoice import FiscalElectronicBondValidator


class WsbfeInvoiceDetails(object):
    """
    Se encarga de asignar los detalles de una invoice en
    los factories de WSBFE.

    :param wsbfe: Objeto Wsbfe.
    :param invoice: Objeto ElectronicInvoice para tomar los detalles.
    :param pos: Numero de punto de venta.
    """

    def __init__(self, wsbfe, invoice, pos):
        self.wsbfe = wsbfe
        self.pos = pos
        self.invoice = invoice
        self.detail = None

    def get_details(self):
        """ Devuelve los detalles completos para esa factura """

        self._set_details()
        return self.detail

    def _set_details(self):
        """ Completa los detalles a enviar segun los datos del documento """

        last_document_req = self.wsbfe.get_last_number(self.pos, self.invoice.document_code)
        self.detail = self._get_document_request()
        self.detail.Id = self.wsbfe.get_last_id().BFEResultGet.Id + 1
        self.detail.Tipo_doc = self.invoice.customer_document_type
        self.detail.Nro_doc = self.invoice.customer_document_number
        self.detail.Zona = self.invoice.zone_id
        self.detail.Tipo_cbte = self.invoice.document_code
        self.detail.Punto_vta = self.pos
        self.detail.Cbte_nro = last_document_req + 1
        self.detail.Imp_total = self.invoice.get_total_amount()
        self.detail.Imp_tot_conc = self.invoice.untaxed_amount
        self.detail.Imp_neto = self.invoice.taxed_amount
        self.detail.Impto_liq = self.invoice.pay_off_tax_amount
        self.detail.Impto_liq_rni = self.invoice.rni_pay_off_tax_amount
        self.detail.Imp_op_ex = self.invoice.exempt_amount
        self.detail.Imp_perc = self.invoice.reception_amount
        self.detail.Imp_iibb = self.invoice.iibb_amount
        self.detail.Imp_perc_mun = self.invoice.municipal_reception_amount
        self.detail.Imp_internos = self.invoice.internal_tax_amount
        self.detail.Imp_moneda_Id = self.invoice.mon_id
        self.detail.Imp_moneda_ctz = round(self.invoice.mon_cotiz, 6)
        self.detail.Fecha_cbte = self.invoice.document_date
        self._set_items()



    def _serialize_item(self, item):
        return self._get_item()(
            Pro_codigo_ncm=item.codigo_prod_ncm,
            Pro_ds=item.description,
            Pro_qty=item.quantity,
            Pro_umed=item.measurement_unit,
            Pro_precio_uni=item.unit_price,
            Imp_bonif=item.bonification,
            Imp_total=item.total_price,
            Iva_id=item.iva_id,
        )

    def _set_items(self):
        if self.invoice.array_items:
            self.detail.Items = self._get_item_array()([
                self._serialize_item(item) for item in self.invoice.array_items
            ])

    def _get_document_request(self):
        return Client(self.wsbfe.url).type_factory('ns0').ClsBFERequest()

    def _get_item_array(self):
        return Client(self.wsbfe.url).get_type('ns0:ArrayOfItem')

    def _get_item(self):
        return Client(self.wsbfe.url).get_type('ns0:Item')


class Wsbfe(object):
    """
    Bono Fiscal Electrónico.

    :param access_token: AccessToken - Token de acceso
    :param cuit: Cuit de la empresa
    :param homologation: Homologacion si es True
    :param url: Url de servicios para Wsbfe
    """

    def __init__(self, access_token, cuit, homologation=True, url=None):

        if not url:
            self.url = config.service_urls.get('wsbfev1_homologation') if homologation \
                else config.service_urls.get('wsbfev1_production')
        else:
            self.url = url

        self.accessToken = access_token
        self.cuit = cuit
        self.auth_request = self._create_auth_request()

    def get_cae(self, invoices, pos):
        """
        :param invoices: Conjunto de Objetos FiscalElectronicBond, documentos a enviar a AFIP.
        :param pos: Numero de punto de venta.
        :returns str: Respuesta de AFIP sobre la validacion del documento.
        """

        # TODO: Ver como integramos el get_cae para ambos servicios
        self._validate_invoices(invoices)

        responses = []
        requests = []
        for invoice in invoices:
            request = self._create_cae_request(invoice, pos)
            response = Client(self.url).service.BFEAuthorize(self.auth_request, request)
            self._check_for_errors(response)
            responses.append(response)
            requests.append(request)
        return responses, requests

    def check_webservice_status(self):
        """
        Consulta el estado de los webservices de BFE de AFIP
        :raises Exception: Si alguno de los servidores esta caido
        """

        res = Client(self.url).service.BFEDummy()
        if res.AppServer != 'OK':
            raise Exception('El servidor de aplicaciones no se encuentra disponible. Intente mas tarde.')
        if res.DbServer != 'OK':
            raise Exception('El servidor de base de datos no se encuentra disponible. Intente mas tarde.')
        if res.AuthServer != 'OK':
            raise Exception('El servidor de auntenticacion no se encuentra disponible. Intente mas tarde.')

        return res

    def get_last_number(self, pos_number, document_code):
        """ Recupera el ultimo comprobante autorizado """

        last_document_req = self._set_last_document(pos_number, document_code)
        request = Client(self.url).service.BFEGetLast_CMP(last_document_req)

        self._check_for_errors(request)

        return request.BFEResult_LastCMP.Cbte_nro

    def get_last_id(self):
        """" Recupera el ultimo ID y su fecha """

        request = Client(self.url).service.BFEGetLast_ID(self.auth_request)
        self._check_for_errors(request)

        return request

    def get_measurement_units(self):
        """ Devuelve las unidades de medida y su codigo """

        request = Client(self.url).service.BFEGetPARAM_UMed(self.auth_request)
        self._check_for_errors(request)

        return request

    def get_currencies(self):
        """ Recupera el listado de monedas y su codigo utilizable """

        request = Client(self.url).service.BFEGetPARAM_MON(self.auth_request)
        self._check_for_errors(request)

        return request

    def get_document_codes(self):
        """ Recupera el listado de los tipos de comprobante y su codigo utilizables """

        request = Client(self.url).service.BFEGetPARAM_Tipo_Cbte(self.auth_request)
        self._check_for_errors(request)

        return request

    def get_product_types_ncm(self):
        """Recupera el listado de los tipos de productos según el Nomenclador Común del Sur"""

        request = Client(self.url).service.BFEGetPARAM_NCM(self.auth_request)
        self._check_for_errors(request)

        return request

    def get_zones_codes(self):
        """Recupera el listado de los códigos de zonas"""

        request = Client(self.url).service.BFEGetPARAM_Zonas(self.auth_request)
        self._check_for_errors(request)

        return request

    def get_iva_types(self):
        """Recupera el listado de los tipos de IVA y sus códigos utilizables"""

        request = Client(self.url).service.BFEGetPARAM_Tipo_IVA(self.auth_request)
        self._check_for_errors(request)

        return request

    def _create_cae_request(self, invoice, pos):
        """
        :param invoice: FiscalElectronicBond.
        :param pos: Numero de punto de venta.
        :returns: BFERequest / Envio de documentos para recibir el CAE.
        """

        return WsbfeInvoiceDetails(self, invoice, pos).get_details()

    def _set_last_document(self, pos_number, document_code):
        ClsBFE_LastCMP = Client(self.url).get_type('ns0:ClsBFE_LastCMP')

        last_document_req = ClsBFE_LastCMP(
            Token=self.auth_request.Token,
            Sign=self.auth_request.Sign,
            Cuit=self.auth_request.Cuit,
            Pto_venta=pos_number,
            Tipo_cbte=document_code
        )
        return last_document_req

    def show_error(self, response):
        if response.BFEErr.ErrMsg != 'OK':
            raise AfipError.parse_error(response)

    @staticmethod
    def _validate_invoices(invoices):
        invoiceValidator = FiscalElectronicBondValidator()
        for invoice in invoices:
            invoiceValidator.validate_invoice(invoice)

    @staticmethod
    def _check_for_errors(request):
        if request.BFEErr.ErrMsg != 'OK':
            raise AfipError.parse_error(request)

    def _create_auth_request(self):
        """ Setea el ClsBFEAuthRequest, necesario para utilizar el resto de los metodos """

        ClsBFEAuthRequest = Client(self.url).get_type('ns0:ClsBFEAuthRequest')
        # ns0:ClsBFEAuthRequest(Token: xsd:string, Sign: xsd:string, Cuit: xsd:long)

        auth_request = ClsBFEAuthRequest(
            Token=self.accessToken.token,
            Sign=self.accessToken.sign,
            Cuit=self.cuit
        )
        return auth_request
