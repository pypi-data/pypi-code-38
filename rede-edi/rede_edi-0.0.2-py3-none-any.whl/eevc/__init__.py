import json
from .models import (
    Header, HeaderMatriz, RegistroAjustesCredito,
    RegistroAVS, RegistroCVNSUDolar, RegistroCVNSUParceladoIata,
    RegistroCVNSUParceladoIataEcommerce, RegistroCVNSUParceladoSemJuros,
    RegistroCVNSUParceladoSemJurosEcommerce, RegistroCVNSURecarga,
    RegistroCVNSURotativo, RegistroCVNSURotativoEcommerce,
    RegistroParceladoIata, RegistroParceladoSemJuros,
    RegistroRequest, RegistroRequestEcommerce, RegistroRVDolar,
    RegistroRVIata, RegistroRVParceladoSemJuros, RegistroRVRotativo,
    RegistroSecureCode, RegistroSerasa, RegistroTotalizadorMatriz,
    RegistroTrailerArquivo
)

class LineTypes:
    conf = {
        "CABECALHO" : 
            ( 2, 
            (3, 11, 19, 49, 71, 77, 86, 101, 121, 1024), 
            Header ),
        "CABECALHO_MATRIZ" : ( 4, (3, 12, 34), HeaderMatriz),
        "REGISTRO_REQUEST" : 
            (5, 
            (3, 12, 21, 37, 52, 60, 75, 90, 102, 108, 112, 120, 121, 1024), 
            RegistroRequest),
        "REGISTRO_REQUEST_ECOMMERCE" : 
            (33, 
            (3,12,21,37,45,57,63,83,113), 
            RegistroRequestEcommerce),
        "REGISTRO_RV_ROTATIVO" : 
            (6, 
            (3,12,21,24,29,40,48,53,68,83,98,113,128,136,137), 
            RegistroRVRotativo),
        "REGISTRO_CVNSU_ROTATIVO" : 
            (8, 
            (3,12,21,29,37,52,67,83,86,98,111,126,132,138,154,170,186,202,203,218,226,229,230), 
            RegistroCVNSURotativo),
        "REGISTRO_CVNSU_ROTATIVO_ECOMMERCE" : 
            (34, 
            (3,12,21,29,44,60,72,78,98,128), 
            RegistroCVNSURotativoEcommerce),
        "REGISTRO_CVNSU_RECARGA" : (40, (3,12,21,29,41,56,62,77,78), RegistroCVNSURecarga),
        "REGISTRO_RV_PARCELADO_SEM_JUROS" : 
            (10, 
            (3,12,21,24,29,40,48,53,68,83,98,113,128,136,137), 
            RegistroRVParceladoSemJuros),
        "REGISTRO_AJUSTES_CREDITO" : 
            (11, 
            (3,12,21,29,44,52,67,68,71,77,88,90,118,119), 
            RegistroAjustesCredito),
        "REGISTRO_CVNSU_PARCELADO_SEM_JUROS" : 
            (12, 
            (3,12,21,29,37,52,67,83,86,88,100,113,128,134,140,156,172,188,204,205,220,235,250,258,261,262), 
            RegistroCVNSUParceladoSemJuros),
        "REGISTRO_CVNSU_PARCELADO_SEM_JUROS_ECOMMERCE" :
            (35, 
            (3,12,21,29,44,60,72,78,98,128), 
            RegistroCVNSUParceladoSemJurosEcommerce),
        "REGISTRO_PARCELADO_SEM_JUROS" : 
            (14, 
            (3,12,21,29,37,39,54,69,84,92,1024), 
            RegistroParceladoSemJuros),
        "REGISTRO_RV_IATA" : 
            (16, 
            (3,12,21,24,29,40,48,53,68,83,98,113,128,136,137), 
            RegistroRVIata),
        "REGISTRO_AVS" : 
            (17, 
            (3,12,17,25), 
            RegistroAVS),
        "REGISTRO_CVNSU_PARCELADO_IATA" : 
            (18, 
            (3,12,21,29,37,52,67,83,86,88,100,113,128,134,140,156,172,188,204,205,220,235,250,258,261,262), 
            RegistroCVNSUParceladoIata),
        "REGISTRO_CVNSU_PARCELADO_IATA_ECOMMERCE" : 
            (36, 
            (3,12,21,29,44,60,72,78,98,128), 
            RegistroCVNSUParceladoIataEcommerce),
        "REGISTRO_SERASA" : 
            (19, 
            (3,12,17,25), 
            RegistroSerasa),
        "REGISTRO_PARCELAS_IATA" : 
            (20, 
            (3,12,21,29,37,39,54,69,84,92,1024), 
            RegistroParceladoIata),
        "REGISTRO_SECURECODE" : (21, (3,12,17,25,26), RegistroSecureCode),
        "REGISTRO_RV_DOLAR" : 
            (22, 
            (3,12,21,24,29,40,48,53,68,83,98,113,128,136,137), 
            RegistroRVDolar),
        "REGISTRO_CVNSU_DOLAR" : 
            (24, 
            (3,12,21,29,37,52,67,83,86,95,103,115,128,143,149,155,163,165,167,169), 
            RegistroCVNSUDolar),
        "REGISTRO_TOTALIZADOR_MATRIZ" : 
            (26, 
            (3,12,27,33,48,63,78,93,108,123,138,153,168,174), 
            RegistroTotalizadorMatriz),
        "REGISTRO_TRAILER_ARQUIVO" : 
            (28, 
            (3,7,13,22,37,43,58,73,88,103,118,133,148,163,178,184), 
            RegistroTrailerArquivo)
    }

class Eevc:
    
    def __init__(self, filelocation):
        self.filelocation = filelocation
        headerdata = self._get_header_data()
        self.info = {
            'tipo_arquivo': 'EEVC',
            'versao': headerdata.get('VERSAO_ARQUIVO'),
            'qtde_linhas': self._qtde_linhas()
        }

    def _get_value_from_line(self, line, layout):
        anterior = None
        retorno = []
        for quebra in layout:
            retorno.append(line[anterior:quebra].strip())
            anterior = quebra

        return retorno

    def _get_header_data(self):
        with open(self.filelocation, 'r') as f:
            for line in f:
                return self.get_line_data(line)
                break

    @staticmethod
    def del_none(d):
        """
        Delete keys with the value ``None`` in a dictionary, recursively.

        This alters the input so you may wish to ``copy`` the dict first.
        """
        for key, value in list(d.items()):
            if value is None:
                del d[key]
            elif value == '':
                del d[key]
            elif isinstance(value, dict):
                del_none(value)
        return d  

    def get_line_data(self, line):

        tipo = int(line[:3])

        for k, v in LineTypes.conf.items():
            if v[0] == tipo:
                retorno = dict(zip(v[2].COLUMNS, self._get_value_from_line(line, v[1])))
                retorno['DS_TIPO_REGISTRO'] = k
                return Eevc.del_none(retorno)

        return {}

    def _qtde_linhas(self):
        i = 0
        with open(self.filelocation, 'r') as f:
            for line in f:
                i = i + 1

        return i
