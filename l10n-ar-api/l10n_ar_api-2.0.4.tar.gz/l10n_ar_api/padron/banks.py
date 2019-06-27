try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

from unidecode import unidecode
from l10n_ar_api.padron.contributor import Contributor


class Banks:
             
    @staticmethod
    def get_banks_list():
        """
        Obtiene la lista de bancos desde AFIP utilizando
        la libreria BeautifulSoup para webscraping
        """

        url = 'http://www.afip.gov.ar/genericos/emisorasGarantias/formularioCompa%C3%B1ias.asp?completo=1&ent=3'
        req = urllib.Request(url)
        f = urllib.urlopen(req)
        soup = BeautifulSoup(f)
        table = soup.find('table', attrs={"class": "contenido"})
        banks = []
        for row in table.findAll('tr')[2:]:
            banks.append([td.text.strip() for td in row.findAll('td') if td.text.strip()])
                        
        return banks

    @staticmethod
    def get_values(banks_list):
        """
        :param banks_list: Lista de bancos.
        :return: Lista de diccionarios con los valores de cada banco
        """
        
        values = []
        for bank_list in banks_list:
            
            bank_values = {}
            
            if bank_list:    
                
                # Validamos el cuit del banco para comprobar existencia
                if Contributor.is_valid_cuit(bank_list[0]):
            
                    bank_values['cuit'] = bank_list[0]
                    bank_values['code'] = bank_list[1]
                    bank_values['name'] = unidecode(bank_list[2])
                    values.append(bank_values)
            
        return values
