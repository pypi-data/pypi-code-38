from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from unicodedata import normalize
from datetime import datetime
import configparser
import argparse
import sys
import os
import shutil

chrome_options = Options()
chrome_options.add_argument('--headless --enable-javascript')
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": r"C:\\",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})
driver = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)

config = configparser.RawConfigParser(allow_no_value=True)
config.read('config.ini', encoding='utf8')
data = dict(config._sections)
for k in data:
    data[k] = dict(config._defaults, **data[k])
    data[k].pop('__name__', None)

servidor = 'servidor_local'
arquivo_dados = ''
cronograma = ''
leiaute = ''
entidade = 'AGENCIA NACIONAL DE TELECOMUNICACOES - SEDE (02.030.715/0001-12)'
ano = datetime.now().year
entrega = ''
formato_arquivo = 'csv'

def go_to(pagina):
    if (not pagina in data['links']):
        raise Exception('Link para %s não encontrado' % pagina)
    print('[%s]: Navegando para %s' %(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),servidor + data['links'][pagina]))
    driver.get(servidor + data['links'][pagina])
    #driver.get(servidor + data['links'][pagina])

def encontra_cronograma():
    go_to('cronograma')

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'formConsulta:nome')))

    nome_cronograma_field = driver.find_element_by_id('formConsulta:nome')
    nome_cronograma_field.clear()
    nome_cronograma_field.send_keys(cronograma)

    ano_field = driver.find_element_by_id('formConsulta:ano')
    ano_field.clear()
    ano_field.send_keys(ano)

    driver.find_element_by_id('formConsulta:btnConsultar').click()

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'formConsulta:nome')))

    cronogramas_tabela = driver.find_elements_by_xpath('//*[@id="formConsulta:resultado:tb"]/tr')
    encontrou_cronograma = False
    for linha in cronogramas_tabela:
        if(cronograma == linha.find_element_by_xpath('td[2]').text):
            if(entidade == linha.find_element_by_xpath('td[3]').text):
                encontrou_cronograma = True
                break
    if(encontrou_cronograma):
        print('[%s]: Encontrado cronograma \'%s\' para entidade %s' %(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),linha.find_element_by_xpath('td[2]').text,entidade))
        linha.find_element_by_xpath('td[10]/span/a').click()
        return True
    else:
        print('[%s]: Não encontrado cronograma \'%s\' para entidade %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),cronograma,entidade))
        return False

def tem_acesso():
    print('[%s]: Verificando se o usuário tem acesso para enviar dados para o cronograma' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="j_id23"]/dt/span')))
        mensagem_erro = driver.find_element_by_xpath('//*[@id="j_id23"]/dt/span').text
        print('[%s]: Mensagem do DICI: %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), mensagem_erro))
        return False
    except:
        print('[%s]: Usuário tem acesso par enviar dados ao cronograma.' % (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        return True

def envia_arquivo():

    global arquivo_dados

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'arquivo')))

    arquivo_field = driver.find_element_by_id("arquivo")
    driver.execute_script("arguments[0].style.display = 'block';", arquivo_field)

    novo_arquivo_dados = renomeia_arquivo()

    arquivo_field.send_keys(novo_arquivo_dados)

    print('[%s]: Enviando arquivo %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), novo_arquivo_dados))

    driver.find_element_by_id("formEdicao:btnSalvar").click()

    try:
        alert = driver.switch_to.alert
        alerta = alert.text
        alert.accept()
        if(alerta == 'Já existe um arquivo enviado com o mesmo nome, enviar este arquivo irá substituí-lo. Deseja continuar?'):
            print('[%s]: Substituindo arquivo anterior.' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, '//*[@id="error-msg"]/dt/span')))
            if(driver.find_element_by_xpath('//*[@id="error-msg"]/dt/span').text == 'Operação realizada com sucesso.'):
                print('[%s]: Arquivo carregado no DICI. Verificar processamento no site.' % (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            else:
                print('[%s]: Erro ao carregar o arquivo. Tente novamente.' % (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        else:
            print('[%s]: Ocorreu algum erro ao carregar o arquivo: %s'%(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), alert.text))
    except NoAlertPresentException:
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, '//*[@id="error-msg"]/dt/span')))
        if (driver.find_element_by_xpath('//*[@id="error-msg"]/dt/span').text == 'Operação realizada com sucesso.'):
            print('[%s]:Arquivo carregado no DICI. Verificar processamento no site.' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        else:
            print('[%s]: Erro ao carregar o arquivo. Tente novamente.' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    if(novo_arquivo_dados != os.path.abspath(arquivo_dados)):
        os.remove(novo_arquivo_dados)

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def renomeia_arquivo():

    nome_correto = (remover_acentos(leiaute) + '-' + str(ano) + '-' + entrega).upper().replace(' ', '_') + '.' + formato_arquivo

    if(arquivo_dados != nome_correto):
        old_name = os.path.abspath(arquivo_dados)
        basedir = os.path.dirname(old_name)
        new_name = os.path.join(basedir, nome_correto)
        shutil.copy(old_name, new_name)
        return new_name

    return os.path.abspath(arquivo_dados)

def determina_variaveis(argv):

    parser = argparse.ArgumentParser(description='Envia Dados ao DICI')
    parser.add_argument('cronograma', type=str,
                        help='Nome do Cronograma do DICI')
    parser.add_argument('leiaute', type=str,
                        help='Nome do Leiaute do DICI')
    parser.add_argument('entrega', type=str,
                        help='Período de Entrega dos Dados. Valores possível são: ' + ', '.join([tipo_entrega for tipo_entrega in data['entrega']]))
    parser.add_argument('--formato_arquivo', type=str, dest='formato_arquivo', default='csv',
                        help='Formato do Arquivo com dados. Valores possível são: ' + ', '.join([tipo_entrega for tipo_entrega in data['formato']]) + '. Se não informado será csv')
    parser.add_argument('--arquivo_dados', type=str, dest='arquivo_dados',
                        help='Caminho para o arquivo com os dados a serem enviados ao DICI. Se não informado será o padrão do cronograma.')
    parser.add_argument('--entidade', type=str, default=entidade,
                        dest='entidade', help='Entidade Responsável pelo Envio. Se não informado será Anatel.')
    parser.add_argument('--ano', type=int, default=ano, dest='ano',
                        help='Ano de Entrega dos Dados. Se não informado será o ano corrente.')
    parser.add_argument('--servidor', type=str, default=servidor, dest='servidor',
                        help='Servidor do DICI a ser utilizado. Valores possível são: ' + ', '.join([tipo_entrega for tipo_entrega in data['dici']]) + '. Se não informado será servidor_local')

    argumentos = vars(parser.parse_args(argv[1:]))
    return argumentos

def obtem_variaveis(argumentos):

    global servidor, cronograma, entidade, arquivo_dados, ano, entrega, data, formato_arquivo, leiaute

    cronograma = argumentos['cronograma']
    entidade = argumentos['entidade']
    leiaute = argumentos['leiaute']

    if(argumentos['entrega'] in  data['entrega']):
        entrega = data['entrega'][argumentos['entrega']]
    else:
        raise Exception('Tipo de Entrega \'%s\' não encontrado em pyDICI/config.ini' %argumentos['entrega'])

    ano = argumentos['ano']

    if (argumentos['formato_arquivo'] in data['formato']):
        formato_arquivo = argumentos['formato_arquivo']
    else:
        raise Exception(
            'Tipo de Formato do Arquivo \'%s\' não encontrado em pyDICI/config.ini' % argumentos['formato_arquivo'])

    if argumentos['arquivo_dados'] == None:
        arquivo_dados = (remover_acentos(leiaute) + '-' + str(ano) + '-' + entrega).upper().replace(' ', '_') + '.' + formato_arquivo
    else:
        arquivo_dados = argumentos['arquivo_dados']
        base, formato_arquivo = os.path.splitext(arquivo_dados)
        formato_arquivo = formato_arquivo[1:]

    if(not os.path.isfile(arquivo_dados)):
        raise Exception('Arquivo %s não encontrado' %arquivo_dados)

    if(argumentos['servidor'] in data['dici']):
        servidor = data['dici'][argumentos['servidor']]
    else:
        raise Exception('Servidor \'%s\' não encontrado em pyDICI/config.ini' % argumentos['servidor'])

def enviar(cronograma, leiaute, entrega, arquivo_dados=None, formato_arquivo='csv', entidade=entidade, ano=ano, servidor=servidor, teste=False):
    print('[%s]: Iniciando execução do pyDICI' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    argumentos = {'cronograma': cronograma,
                  'leiaute': leiaute,
                  'entrega': entrega,
                  'arquivo_dados': arquivo_dados,
                  'formato_arquivo': formato_arquivo,
                  'entidade': entidade,
                  'ano': ano,
                  'servidor': servidor}

    if(not teste):
        obtem_variaveis(argumentos)

    try:
        if(encontra_cronograma()):
            if(tem_acesso()):
                envia_arquivo()
    finally:
        driver.quit()
        print('[%s]: Finalizando execução do pyDICI' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def help():
    determina_variaveis(['','-h'])

def main(argv):
    obtem_variaveis(determina_variaveis(argv))
    enviar(cronograma, leiaute, entrega, arquivo_dados, formato_arquivo, entidade, ano, servidor, True)

if(__name__ == "__main__"):
    main(sys.argv)