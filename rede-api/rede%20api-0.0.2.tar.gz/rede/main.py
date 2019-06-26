# coding: utf-8
from datetime import datetime 
from .exceptions import RequestGetError
import json
import os 
import requests 
import sys 

BASE_URL_HOMOLOG = 'https://api-hom.userede.com.br/redelabs'
BASE_URL_DEV = None
BASE_URL = None

class AuthorizationToken:

    def __init__(self, user, password, token, sandbox=True):
        self.token = token
        self.user = user 
        self.password = password
        self.header_authorization = {
            'Accept': '*/*',
            'Authorization': self.token,
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'host': 'api-hom.userede.com.br',
            'accept-encoding': 'gzip, deflate',
            'content-length': '74'
        }
        self.payload = 'grant_type=password&username='+user+'&password='+password

    def createToken(self):

        r = requests.post(
            'https://api-hom.userede.com.br/redelabs/oauth/token',
            headers=self.header_authorization,
            data=self.payload)

        assert (r.status_code == 200),"Token request error"

        return json.loads(r.text) 


class Parameters:

    @staticmethod
    def parseParametersToUrl(**kwargs):
        params = ''
        for i, (k, v) in enumerate(kwargs.items()):
            sep = '?' if i == 0 else '&'
            params = ''.join([params,sep,k,'=',v])

        return params


class RequestsConciliacao:

    def __init__(self, user, password, token):
        # Somente implementado métodos de homologação
        auth = AuthorizationToken(user, password, token, True)
        self.authorization = auth.createToken()
        self.token = self.authorization.get('token_type') + ' ' + self.authorization.get('access_token')

        self.header_request = {
            'content-type': 'application/json',
            'Authorization': self.token
        }

        self.urlbase = BASE_URL_HOMOLOG

    def get(self, url, params: dict):
        print(self.header_request)
        r = requests.get(self.urlbase+url, headers=self.header_request, params=params)

        if r.status_code != requests.codes.ok:
            raise RequestGetError(r.status_code, r.text)

        return r.json()

    def post(self, url, params, data=None):

        r = requests.post(self.urlbase+url, headers=self.header_request, params=params, data=data)

        if r.status_code != requests.codes.ok:
            raise RequestGetError(r.status_code, r.text)

        return r.json()

    def put(self, url, data=None):
        r = requests.post(self.urlbase+url, headers=self.header_request, data=data)

        if r.status_code != requests.codes.ok:
            raise RequestGetError(r.status_code, r.text)

        return r.json()

    # C O N C I L I A C A O 
    def consultarVendas(self, params: dict):
        return self.get('/conciliation/v1/sales', params)  

    def consultarParcelas(self, params: dict):
        return self.get('/conciliation/v1/sales/installments', params) 

    def consultarPagamentosSumarizadosCIP(self, params:dict):
        return self.get('/conciliation/v1/payments', params) 

    def _consultarpagamentosOrdemCredito(self, **kwargs):
        # MÉTODO ESTÁ COMO PRIVADO POIS ESTÁ EM CONSTRUÇÃO POR PARTE DA REDE
        pass 

    def _consultarRecebiveis(self, **kwargs):
        # MÉTODO ESTÁ COMO PRIVADO POIS ESTÁ EM CONSTRUÇÃO POR PARTE DA REDE
        pass 

    def consultarRecebiveisSumarizados(self, params):
        url = '/conciliation/v1/receivables/summary' 
        return self.get(url, params)

    def consultarDebitos(self, params: dict):
        return self.get('/conciliation/v1/charges', params)

    def _consultarDebitosSumarizados(self, params: dict):
        # MÉTODO ESTÁ COMO PRIVADO POIS ESTÁ EM CONSTRUÇÃO POR PARTE DA REDE
        url = '/conciliation/v1/charges/summary' 
        return self.get(url, None)

    def consultarListaAjusteDebitos(self):
        # MÉTODO COM ERRO DO LADO DA REDE...
        url = '/conciliation/v1/charges/adjustment-types' 
        return self.get(url, None)


    # C R E D E N C I A M E N T O
    def criarPropostaCredenciamento(self, data: dict):
        url = '/proposal/v1/affiliates' 
        return self.post(url, None, data)

    def consultarPropostaCredenciamentoPorId(self, id: str):
        url = '/proposal/v1/affiliates/{id}'.format(id=id) 
        return self.get(url)

    def consultarEstabelecimentoComercial(self, params: dict):
        url = '/customer/v1/merchants'
        return self.get(url, params)

    def cancelarEstabelecimentoComercial(self, id: int):
        url = '/customer/v1/merchants/{id}/cancel'.format(id=str(id))
        url = url
        return self.put(url)

    def consultarPrecos(self, params: dict):
        url = '/proposal/v1/pricing' 
        return self.get(url, params)

    def consultarMCCs(self, params: dict):
        url = '/brand/v1/mcc'
        return self.get(url, params) 

    def createLeadCredenciamento(self, params: dict, data: dict):
        url = '/proposal/v1/lead'
        return self.post(url, params, data) 


