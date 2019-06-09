import json
import requests

from .utils import B64Utils


class PyBerdrola:
    def __init__(self, user, password):
        self._user = user
        self._password = password
        self._token = None
        self._cookie = None

    def login(self):
        """
        Does the loggin in the platform and stores both token and cookies to the following requests
        """
        URL_LOGIN = "https://www.iberdrola.es/webcli/preLogin"
        req_login = requests.post(URL_LOGIN, auth=(self._user, self._password))
        self._token = req_login.json()["jwtToken"]
        self._cookie = req_login.headers["Set-Cookie"]

    def _headers_for_request(self):
        return {
            "Cookie": self._cookie,
            "Auth-Token": self._token,
            "Plataforma": "iOS",
            "Version": "11007",
            "Content-Type": "application/json",
        }

    def data(self):
        """
        Returns all the customer data (list of clients, contracts, etc.)
        """
        URL_DATA = "https://www.iberdrola.es/webcli/appesp/usuario/data"
        req_data = requests.post(URL_DATA, headers=self._headers_for_request())

        return req_data.json()

    def last_invoice(self):
        """
        Returns a summary of the last invoices, grouped by year.
        """
        URL_LAST_INVOICE = "https://www.iberdrola.es/webcli/appesp/facturas/ultimafactura"
        req_last_invoice = requests.post(
            URL_LAST_INVOICE, headers=self._headers_for_request())
        return req_last_invoice.json()

    def all_invoices(self):
        """
        Returns a list of all available invoices
        """
        URL_LIST = "https://www.iberdrola.es/webcli/appesp/facturas/lista"
        req_list = requests.post(URL_LIST, headers=self._headers_for_request())
        return req_list.json()

    def download_invoice(self, invoice, save=False, file_name=None):
        """
        Returns all information about the selected invoice. It"s also possible to download the PDF with this data.
        """
        URL_DOWNLOAD = "https://www.iberdrola.es/webcli/appesp/facturas/descarga"
        req_download = requests.post(URL_DOWNLOAD,
                                     headers=self._headers_for_request(),
                                     data=json.dumps({
                                         "indice": 0,
                                         "numFactura": invoice
                                     }))

        download_res = req_download.json()

        if save:
            file_name = file_name or download_res["nombrePdf"]
            B64Utils.file_from_base64(
                download_res["pdfData"], "invoices/" + file_name)
            return None

        # As this result could be printed, I'm overriding temporally
        download_res["pdfData"] = "*********removed*********"
        return download_res
