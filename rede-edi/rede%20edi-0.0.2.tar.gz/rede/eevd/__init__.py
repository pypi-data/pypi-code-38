from .models import ( 
    Header, SalesSummary, TotalPointSales, TotalHolder,
    TotalFile, DetailsSalesReceipt, DetailsSalesReceiptEcommerce,
    DetailsReceipt, DisaggregationPreDatedSales,
    LiquidatedPreDatedTransactions, AdjustmentsNet,
    AdjustmentsNetEcommerce
)

class LineTypes:
    CABECALHO = 0
    RESUMO_VENDAS = 1
    TOTAL_PONTO_VENDAS = 2
    TOTAL_MATRIZ = 3
    TOTAL_ARQUIVO = 4
    DETALHES_COMPROVANTE_VENDAS = 5
    DETALHES_COMPROVANTE_VENDAS_ECOMMERCE = 13
    RECEIPTS_DETAILS =20
    DESAGENDAMENTO_VENDAS_PREDATADAS = 8
    TRANSACOES_PREDATADAS_LIQUIDADAS = 9
    AJUSTES_NET = 11
    AJUSTES_NET_ECOMMERCE = 17 


class Eevd:

    def __init__(self, filelocation):
        self.filelocation = filelocation
        self.CABECALHO = self._get_header()
        self.resumo = {}
        self.info = {
            'qtde_linhas' : self._file_len(),
            'resumo': self.resumo,
            'versao': self.CABECALHO.get('VERSAO_ARQUIVO'),
            'tipo_arquivo': 'EEVD'
        }

    def get_line_data(self, line):
        tipolinha = self._get_item_name(int(line[:2]))
        classe = self._get_class_per_linetype(tipolinha)
        item = dict(zip(classe.COLUMNS, line.strip().split(',')))
        item['DS_TIPO_REGISTRO'] = tipolinha
        return item

    def _get_class_per_linetype(self, linetype):
        mapa = {
            'CABECALHO': Header,
            'RESUMO_VENDAS': SalesSummary,
            'TOTAL_PONTO_VENDAS': TotalPointSales,
            'TOTAL_MATRIZ': TotalHolder,
            'TOTAL_ARQUIVO': TotalFile,
            'DETALHES_COMPROVANTE_VENDAS': DetailsSalesReceipt,
            'DETALHES_COMPROVANTE_VENDAS_ECOMMERCE': DetailsSalesReceiptEcommerce,
            'DETALHES_COMPROVANTES': DetailsReceipt,
            'DESAGENDAMENTO_VENDAS_PREDATADAS': DisaggregationPreDatedSales,
            'TRANSACOES_PREDATADAS_LIQUIDADAS': LiquidatedPreDatedTransactions,
            'AJUSTES_NET': AdjustmentsNet,
            'AJUSTES_NET_ECOMMERCE': AdjustmentsNetEcommerce
        }

        for k, v in mapa.items():
            if k == linetype:
                return v

        raise

    def get_list_methods_read_line(self, tipolinha = None):

        mapa = {
            'CABECALHO': self._get_header,
            'RESUMO_VENDAS': self.get_RESUMO_VENDAS,
            'TOTAL_PONTO_VENDAS': self.get_total_point_sales,
            'TOTAL_MATRIZ': self.get_total_holder,
            'TOTAL_ARQUIVO': self.get_total_file,
            'DETALHES_COMPROVANTE_VENDAS': self.get_sales_DETALHES_COMPROVANTES,
            'DETALHES_COMPROVANTE_VENDAS_ECOMMERCE': self.get_DETALHES_COMPROVANTES_sales_ecommerce,
            'DETALHES_COMPROVANTES': self.get_receipts_details,
            'DESAGENDAMENTO_VENDAS_PREDATADAS': self.get_DESAGENDAMENTO_VENDAS_PREDATADAS,
            'TRANSACOES_PREDATADAS_LIQUIDADAS': self.get_TRANSACOES_PREDATADAS_LIQUIDADAS,
            'AJUSTES_NET': self.get_AJUSTES_NET,
            'AJUSTES_NET_ECOMMERCE': self.get_AJUSTES_NET_ecommerce
        }

        if not tipolinha == None:
            for k, v in mapa.items():
                if k == tipolinha:
                    return v

        return mapa

    def _get_header(self):
        with open(self.filelocation, 'r') as f:
            for line in f:
                return Header.read(line)

    def _set_resumo(self, item):
        if self.resumo.get(item, {}) == {}:
            self.resumo[item] = 1
        else:
            self.resumo[item] = self.resumo[item] + 1
        

    def get_RESUMO_VENDAS(self):
        return self._get_data(LineTypes.RESUMO_VENDAS, SalesSummary)
        
    def get_total_point_sales(self):
        return self._get_data(LineTypes.TOTAL_PONTO_VENDAS, TotalPointSales)

    def get_total_holder(self):
        return self._get_data(LineTypes.TOTAL_MATRIZ, TotalHolder)

    def get_total_file(self):
        return self._get_data(LineTypes.TOTAL_ARQUIVO, TotalFile)

    def get_sales_DETALHES_COMPROVANTES(self):
        return self._get_data(LineTypes.DETALHES_COMPROVANTE_VENDAS, DetailsSalesReceipt) 

    def get_DETALHES_COMPROVANTES_sales_ecommerce(self):
        return self._get_data(LineTypes.DETALHES_COMPROVANTE_VENDAS_ECOMMERCE, DetailsSalesReceiptEcommerce) 

    def get_receipts_details(self):
        return self._get_data(LineTypes.RECEIPTS_DETAILS, DetailsReceipt)  

    def get_DESAGENDAMENTO_VENDAS_PREDATADAS(self):
        return self._get_data(LineTypes.DESAGENDAMENTO_VENDAS_PREDATADAS, DisaggregationPreDatedSales)  

    def get_TRANSACOES_PREDATADAS_LIQUIDADAS(self):
        return self._get_data(LineTypes.TRANSACOES_PREDATADAS_LIQUIDADAS, LiquidatedPreDatedTransactions)  

    def get_AJUSTES_NET(self):
        return self._get_data(LineTypes.AJUSTES_NET, AdjustmentsNet)   

    def get_AJUSTES_NET_ecommerce(self):
        return self._get_data(LineTypes.AJUSTES_NET_ECOMMERCE, AdjustmentsNetEcommerce)

    def _get_item_name(self, num):
        for k, v in LineTypes.__dict__.items():
            if num == v:
                return k

    def _get_data(self, typeline, lineclass):
        return_data = []
        for item in self._readfile(typeline):
            return_data.append(dict(zip(lineclass.COLUMNS, item)))
        return return_data

    def _get_single_data(self, lineclass, line):
        return dict(zip(lineclass.COLUMNS, line.strip().split(',')))


    def _readfile(self, linetype):
        with open(self.filelocation, 'r') as f:
            for line in f:
                lineinfo = line.strip().split(',')
                if int(lineinfo[0]) == linetype:
                    yield lineinfo

    def _file_len(self):
        with open(self.filelocation) as f:
            for i, l in enumerate(f):
                # print(l.split(',')[0])
                self._set_resumo( self._get_item_name(int(l.split(',')[0])) )
                pass
        return i + 1
