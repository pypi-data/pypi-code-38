import json

from .models import (
    AjustesCredito, AjustesDebito, AjustesDebitoEcommerce,
    AjustesNet, AjustesNetEcommerce, Antecipacoes, Avs,
    Creditos, DebitosLiquidados, DebitosLiquidadosEcommerce,
    DebitosPendentes, DebitosPendentesEcommerce, DesagendamentoParcelas,
    DesagendamentoParcelasEcommerce, Header, HeaderMatriz, SecureCode,
    Serasa, TotalizadorCreditos, TotalizadorMatriz, TrailerArquivo
)

class LineTypes:
    conf = {
        "CABECALHO": (
            30,
            (3, 11, 19, 53, 75, 81, 90, 105, 125),
            Header
        ),
        "CABECALHO_MATRIZ": (
            32,
            (3, 12, 34),
            HeaderMatriz
        ),
        "CREDITOS": (
            34,
            (3, 12, 23, 31, 46, 47, 50, 56, 67, 75, 84, 
            92, 93, 94, 109, 124, 129, 131, 140),
            Creditos
        ),
        "AJUSTES_NET": (
            35,
            (3,12,21,29,44,45,47,75,91,99,108,123,
            131,137,146,154,169,170,178,193,208,223,
            238,250,256,257,268,283,298,299,30),
            AjustesNet
        ),
        "AJUSTES_NET_ECOMMERCE": (
            53,
            (3,19,27,36,45,60,72,78,98,128),
            AjustesNetEcommerce
        ),
        "ANTECIPACOES": (
            36,
            (3,12,23,31,46,47,50,56,67,76,84,
            99,107,112,127,142,151,152),
            Antecipacoes
        ),
        "TOTALIZADOR_CREDITOS": (
            37,
            (3,12,19,27,42,43,46,52,63,71,79,94),
            TotalizadorCreditos
        ),
        "AJUSTES_DEBITO": (
            38,
            (3,12,23,31,46,47,50,56,67,76,84,99,
            101,129,145,160,166,174,189,204,213,
            221,233,242,250,265,271,272,287,302,303),
            AjustesDebito
        ),
        "AJUSTES_DEBITO_ECOMMERCE": (
            54,
            (3,12,28,37,45,57,72,78,98,128),
            AjustesDebitoEcommerce
        ),
        "SERASA": (
            40,
            (3,12,17,32,40,48,63),
            Serasa
        ),
        "AVS": (
            41,
            (3,12,17,32,40,48,63),
            Avs
        ),
        "SECURECODE": (
            42,
            (3,12,17,32,40,48,63,64),
            SecureCode
        ),
        "AJUSTES_CREDITO": (
            43,
            (3,12,21,32,40,48,63,64,67,73,84,86,114,115),
            AjustesCredito
        ),
        "DEBITOS_PENDENTES": (
            44,
            (3,12,23,31,46,48,76,92,104,112,118,133,142,150,159,
            174,182,197,203,218,226,241,256,258,286,287),
            DebitosPendentes
        ),
        "DEBITOS_PENDENTES_ECOMMERCE": (
            55,
            (3,19,31,39,45,60,69,78,98,128),
            DebitosPendentesEcommerce
        ),
        "DEBITOS_LIQUIDADOS": (
            45,
            (3,12,23,31,46,48,76,92,104,112,118,133,142,
            150,159,174,182,197,203,218,226,241,243,271,
            272),
            DebitosLiquidados
        ),
        "DEBITOS_LIQUIDADOS_ECOMMERCE": (
            56,
            (3,19,31,39,45,60,69,78,98,128),
            DebitosLiquidadosEcommerce
        ),
        "DESAGENDAMENTO_PARCELAS": (
            49,
            (3,12,21,36,44,59,74,89,97,112,127,
            143,151,163,164,166,167),
            DesagendamentoParcelas
        ),
        "DESAGENDAMENTO_PARCELAS_ECOMMERCE": (
            57,
            (3,12,21,112,143,151,163,166,196),
            DesagendamentoParcelasEcommerce
        ),
        "TOTALIZADOR_MATRIZ": (
            50,
            (3,12,18,33,39,54,58,73,79,94),
            TotalizadorMatriz
        ),
        "TRAILER_ARQUIVO": (
            52,
            (3,7,13,22,26,41,47,62,66,81,85,100),
            TrailerArquivo
        )
    }

class Eefi:
    
    def __init__(self, filelocation):
        self.filelocation = filelocation
        headerdata = self._get_header_data()
        self.info = {
            'tipo_arquivo': 'EEFI',
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

    def _qtde_linhas(self):
        i = 0
        with open(self.filelocation, 'r') as f:
            for line in f:
                i = i + 1

        return i

        


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
                return Eefi.del_none(retorno)

        return {}