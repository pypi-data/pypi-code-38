from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from unicodedata import normalize
from datetime import datetime
from termcolor import colored
from argparse import ArgumentParser
from sys import argv
from os import path, rename
from pandas import read_excel
from re import search

entregas =['TRIMESTRE_1','TRIMESTRE_2','TRIMESTRE_3','TRIMESTRE_4','Anual','Pontual','MES_1','MES_2','MES_3','MES_4',
           'MES_5','MES_6','MES_7','MES_8','MES_9','MES_10','MES_11','MES_12','BIMESTRE_1','BIMESTRE_2','BIMESTRE_3',
           'BIMESTRE_4','BIMESTRE_5','BIMESTRE_6','SEMESTRE_1','SEMESTRE_2']

formatos=['csv','xml']

servidor_producao = 'http://sistemasnet/dici/'
servidor_homologacao = 'http://sistemasnethm/dici/'
caminho_dici = 'pages/entrada_dados/consultar_entrada_dados.seam'

def __start_driver():

    global driver

    chrome_options = Options()
    chrome_options.add_argument('--headless --enable-javascript --disable-extensions --log-level=3')
    chrome_options.add_experimental_option("prefs", {
      "download.default_directory": r"C:\\",
      "download.prompt_for_download": False,
      "download.directory_upgrade": True,
      "safebrowsing.enabled": True
    })
    driver = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)

def __encontra_cronograma():
    print('[%s]: Acessando o DICI' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    driver.get(servidor + caminho_dici)

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
        print(colored('[%s]: Não foi encontrado cronograma \'%s\' no ano %s e entidade %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),cronograma,ano,entidade),'red'))
        return False

def __tem_acesso():
    print('[%s]: Verificando se o usuário tem acesso para enviar dados para o cronograma' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="j_id23"]/dt/span')))
        mensagem_erro = driver.find_element_by_xpath('//*[@id="j_id23"]/dt/span').text
        print('[%s]: Mensagem do DICI: %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), mensagem_erro))
        return False
    except:
        print('[%s]: Usuário tem acesso para enviar dados ao cronograma.' % (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        return True

def __carregar_no_dici():

    global arquivo_dados

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'arquivo')))

    arquivo_field = driver.find_element_by_id("arquivo")
    driver.execute_script("arguments[0].style.display = 'block';", arquivo_field)

    old_file, novo_arquivo_dados = __renomeia_arquivo()

    arquivo_field.send_keys(novo_arquivo_dados)

    print('[%s]: Enviando arquivo %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), arquivo_dados))

    driver.find_element_by_id("formEdicao:btnSalvar").click()

    tempo_espera = 600

    try:
        alert = driver.switch_to.alert
        alerta = alert.text
        alert.accept()
        if(alerta == 'Já existe um arquivo enviado com o mesmo nome, enviar este arquivo irá substituí-lo. Deseja continuar?'):
            print('[%s]: Substituindo arquivo anteriormente enviado ao DICI.' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            WebDriverWait(driver, tempo_espera).until(EC.presence_of_element_located((By.XPATH, '//*[@id="error-msg"]/dt/span')))
            if(driver.find_element_by_xpath('//*[@id="error-msg"]/dt/span').text == 'Operação realizada com sucesso.'):
                print('[%s]: Arquivo carregado no DICI. Verifique processamento em %s' % (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),driver.current_url))
            else:
                print(colored('[%s]: Erro ao carregar o arquivo. Tente novamente.' % (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')),'red'))
        elif (alerta.startswith('O nome do arquivo não está em um padrão válido.')):
            nome_esperado = search(r'(?i)[a-z\_]+\-[0-9]{4}\-[a-z\_]+\.(?:' + '|'.join(formatos) + ')',alerta).group()
            arquivo_extensao = nome_esperado.split('.')
            extensao_esperada = arquivo_extensao[len(arquivo_extensao)-1]
            nome_esperado = nome_esperado.split('-')
            leiaute_esperado = nome_esperado[0]
            ano_esperado = nome_esperado[1]
            entrega_esperada = nome_esperado[2].split('.')[0]
            if(extensao_esperada.upper() != formato_arquivo.upper()):
                print(colored('[%s]: Extensão do arquivo está errada. Era esperado %s foi recebido %s'%(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), extensao_esperada.upper(), formato_arquivo.upper()), 'red'))
            if(leiaute_esperado.upper() != __remover_acentos(leiaute).replace(' ', '_').upper()):
                print(colored('[%s]: Leiaute do arquivo está errado. Era esperado %s foi recebido %s' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), leiaute_esperado.upper(), __remover_acentos(leiaute).replace(' ', '_').upper()), 'red'))
            if(ano_esperado != str(ano)):
                print(colored('[%s]: Ano do arquivo está errado. Era esperado %s foi recebido %s' % (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ano_esperado, ano), 'red'))
            if(entrega_esperada.upper() != entrega.upper()):
                print(colored('[%s]: Entrega do arquivo está errada. Era esperado %s foi recebido %s' % (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), entrega_esperada, entrega), 'red'))
        else:
            print(colored('[%s]: Ocorreu algum erro ao carregar o arquivo: %s'%(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), alerta), 'red'))
    except NoAlertPresentException:
        WebDriverWait(driver, tempo_espera).until(EC.presence_of_element_located((By.XPATH, '//*[@id="error-msg"]/dt/span')))
        if (driver.find_element_by_xpath('//*[@id="error-msg"]/dt/span').text == 'Operação realizada com sucesso.'):
            print('[%s]: Arquivo carregado no DICI. Verifique processamento em %s' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), driver.current_url))
        else:
            print(colored('[%s]: Erro ao carregar o arquivo. Tente novamente.' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'red'))

    if(novo_arquivo_dados != path.abspath(arquivo_dados)):
        rename(novo_arquivo_dados, path.abspath(arquivo_dados))
    if(old_file):
        rename(novo_arquivo_dados+'.old', novo_arquivo_dados)

def __remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def __renomeia_arquivo():

    nome_correto = (__remover_acentos(leiaute) + '-' + str(ano) + '-' + entrega).upper().replace(' ', '_') + '.' + formato_arquivo

    if(arquivo_dados != nome_correto):
        old_name = path.abspath(arquivo_dados)
        basedir = path.dirname(old_name)
        new_name = path.join(basedir, nome_correto)
        if path.isfile(new_name):
            old_file = True
            rename(new_name, new_name+'.old')
        else:
            old_file = False
        rename(old_name, new_name)
    else:
        new_name = path.abspath(arquivo_dados)
    return old_file, new_name

def __determina_variaveis(argv):

    parser = ArgumentParser(description='Envia Dados ao DICI')
    parser.add_argument(dest='arquivos', type=str,
                        help='Arquivo Excel com a lista de arquivos a serem carregados no DICI. Um arquivo de exemplo se encontra na pasta raiz do pyDICI')
    parser.add_argument('--hm', default=False, action='store_const', const=True,
                        help='Se informado, os dados serão enviados ao servidor de homologação do DICI')

    argumentos = vars(parser.parse_args(argv[1:]))
    arquivos = argumentos['arquivos']
    hm = argumentos['hm']

    return arquivos, hm

def enviar_dados(arquivos, hm=False):
    global arquivos_df, servidor
    global cronograma, entidade, arquivo_dados, ano, entrega, leiaute, formato_arquivo

    print('[%s]: Iniciando execução do pyDICI' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    try:
        __start_driver()

        if (not path.isfile(arquivos)):
            raise Exception('Arquivo %s não encontrado' % arquivos)

        arquivos_df = read_excel(arquivos, columns=['Cronograma','Leiaute','Ano','Entrega','Entidade','Arquivo'])
        if(len(arquivos_df) == 0):
            raise Exception('Não foi encontrado nenhum arquivo de dados em %s' %arquivos)

        print('[%s]: Foram encontrados %s arquivo(s) de dado(s)' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),len(arquivos_df)))

        if(hm):
            servidor = servidor_homologacao
            print('[%s]: Usando servidor de homologação em %s' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), servidor))
        else:
            servidor = servidor_producao
            print('[%s]: Usando servidor de produção em %s' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), servidor))

        for index, arquivo in arquivos_df.iterrows():

            print('[%s]: Carregando %sº arquivo' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), (index + 1)))

            if str(arquivo['Cronograma']) == 'nan':
                raise Exception('Cronograma na posição %s está em branco.' %(index+1))
            if str(arquivo['Leiaute']) == 'nan':
                raise Exception('Leiaute na posição %s está em branco.' % (index+1))
            if str(arquivo['Ano']) == 'nan':
                raise Exception('Ano na posição %s está em branco.' % (index+1))
            if(type(arquivo['Ano']) != int):
                raise Exception('Ano na posição %s deve ser um valor inteiro.' % (index + 1))
            if (len(str(arquivo['Ano'])) != 4):
                raise Exception('Ano na posição %s deve possui 4 digitos.' % (index + 1))
            if str(arquivo['Entrega']) == 'nan':
                raise Exception('Entrega na posição %s está em branco.' % (index+1))
            if not arquivo['Entrega'] in entregas:
                raise Exception('Entrega na posição %s não reconhecida. Foi encontrado \'%s\'. Possíveis valores são: %s' % ((index+1),arquivo['Entrega'],entregas))
            if str(arquivo['Entidade']) == 'nan':
                raise Exception('Entidade na posição %s está em branco.' % (index+1))
            if str(arquivo['Arquivo']) == 'nan':
                raise Exception('Arquivo na posição %s está em branco.' % (index+1))
            if not path.isfile(arquivo['Arquivo']):
                raise Exception('Arquivo de Dados na posição %s não existe' % (index+1))

            base, formato_arquivo = path.splitext(arquivo['Arquivo'])
            formato_arquivo = formato_arquivo[1:]
            if not formato_arquivo in formatos:
                raise Exception('Formato %s não suportado. Formatos atualmente suportados são: %s' %(formato_arquivo,formatos))

            cronograma = arquivo['Cronograma']
            leiaute = arquivo['Leiaute']
            entrega = arquivo['Entrega']
            arquivo_dados = arquivo['Arquivo']
            entidade = arquivo['Entidade']
            ano = arquivo['Ano']

            if (__encontra_cronograma()):
                if (__tem_acesso()):
                    __carregar_no_dici()
    except Exception as e:
        print(colored('[%s]: Ocorreu um erro e o aplicativo será finalizado: %s' % (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(e)), 'red'))
    finally:
        driver.quit()
        print('[%s]: Finalizando execução do pyDICI' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def __main(argv):
    arquivos, hm = __determina_variaveis(argv)
    enviar_dados(arquivos, hm)

if(__name__ == "__main__"):
    __main(argv)