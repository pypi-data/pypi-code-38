#! /usr/bin/env python3
#---------------------------------
#
# Port para Python 3, fix para pontuações, independência da variável HUNPOS_TAGGER
#
# Author: Caio Moraes
# Email: <caiomoraes.cesar@gmail.com>
# GitHub: MoraesCaio
#
# LAViD - Laboratório de Aplicações de Vídeo Digital
#
#---------------------------------
#
# Editado:
#
# Autor: Erickson Silva
# Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>
#
# LAViD - Laboratório de Aplicações de Vídeo Digital
#
#---------------------------------
# Donatus Brazilian Portuguese Parser
#
# Copyright (C) 2010-2013 Leonel F. de Alencar
#
# Author: Leonel F. de Alencar <leonel.de.alencar@ufc.br>
# Homepage: <http://www.leonel.profusehost.net/>
#
# Project's URL: <http://sourceforge.net/projects/donatus/>
# For license information, see LICENSE.TXT
#
# $Id: alexp.py $

"""Este módulo contém funções que permitem utilizar o Aelius para etiquetar uma sentença, construindo entradas lexicais com base nas etiquetas atribuídas às palavras da sentença. Essas entradas lexicais são integradas em uma gramática CFG dada, que é transformada em um parser, utilizado para gerar uma árvore de estrutura sintagmática da sentença.
"""
import re
import nltk
import time
import random
from os import environ, path
from .aelius.Aelius.Extras import carrega
from .aelius.Aelius import AnotaCorpus, Toqueniza
from unicodedata import normalize
from unidecode import unidecode
import argparse
from .char_preprocessing import CharPreprocessing


class ClassificaSentencas:

    def __init__(self):
        self.sentenca_anotada = ""
        self.sleep_times = [0.1, 0.2]

    def toqueniza(self, s):
        """Retorna uma lista de tokens em unicode.
        """
        return Toqueniza.TOK_PORT_LX.tokenize(s)

    def obter_classificacao_morfologica(self):
        return self.sentenca_anotada

    def etiqueta_sentenca(self, s):
        """Aplica um dos etiquetadores do Aelius na etiquetagem da sentença dada como lista de tokens.
        """
        etiquetador = carrega("AeliusHunPos")

        if not environ.get('HUNPOS_TAGGER'):
            current_dir = path.dirname(path.abspath(__file__))
            environ['HUNPOS_TAGGER'] = path.join(current_dir, 'aelius/bin/hunpos-tag')

        anotada = AnotaCorpus.anota_sentencas([s], etiquetador, "hunpos")[0]

        while (anotada[0][1] is None):
            time.sleep(random.choice(self.sleep_times))
            anotada = AnotaCorpus.anota_sentencas([s], etiquetador, "hunpos")[0]

        tag_punctuation = [".", ",", "QT", "("]

        anotada_corrigida = []

        for x in anotada:
            if x[0] == ".":
                anotada_corrigida.append(["[ponto]", "SPT"])
            elif x[0] == "?":
                anotada_corrigida.append(["[interrogação]", "SPT"])
            elif x[0] == "!":
                anotada_corrigida.append(["[exclamação]", "SPT"])
            elif x[1] not in tag_punctuation:
                if x[0] != "":
                    tupla = [x[0].lower(), x[1]]
                    anotada_corrigida.append(tupla)

        return anotada_corrigida

    def gera_entradas_lexicais(self, lista):
        """Gera entradas lexicais no formato CFG do NLTK a partir de lista de pares constituídos de tokens e suas etiquetas.
        """
        entradas = []
        for e in lista:
            # é necessário substituir símbolos como "-" e "+" do CHPTB
            # que não são aceitos pelo NLTK como símbolos não terminais
            c = re.sub(r"[-+]", "_", e[1])
            c = re.sub(r"\$", "_S", c)
            entradas.append("%s -> '%s'" % (c, self.remove_acento(e[0])))
        return entradas

    def corrige_anotacao(self, lista):
        """Esta função deverá corrigir alguns dos erros de anotação mais comuns do Aelius. No momento, apenas é corrigida VB-AN depois de TR.
        """
        i = 1
        while i < len(lista):
            if lista[i][1] == "VB-AN" and lista[i - 1][1].startswith("TR"):
                lista[i] = (lista[i][0], "VB-PP")
            i += 1

    def encontra_arquivo(self):
        """Encontra arquivo na pasta vlibras-translate.
        """
        # if "TRANSLATE_DATA" in environ:
        #     return path.join(environ.get("TRANSLATE_DATA"), "cfg.syn.nltk")
        current_dir = path.dirname(path.abspath(__file__))
        return path.join(current_dir, "cfg.syn.nltk")

    def extrai_sintaxe(self):
        """Extrai gramática armazenada em arquivo cujo caminho é definido relativamente ao diretório nltk_data.
        """
        arquivo = self.encontra_arquivo()
        if arquivo:
            f = open(arquivo, "r")
            sintaxe = f.read()
            f.close()
            return sintaxe
        else:
            print("Arquivo %s não encontrado em nenhum dos diretórios de dados do NLTK:\n%s" % (arquivo, "\n".join(nltk.data.path)))

    def analisa_sentenca(self, sentenca):
        """Retorna lista de árvores de estrutura sintagmática para a sentença dada sob a forma de uma lista de tokens, com base na gramática CFG cujo caminho é especificado como segundo argumento da função. Esse caminho é relativo à pasta nltk_data da instalação local do NLTK. A partir da etiquetagem morfossintática da sentença são geradas entradas lexicais que passam a integrar a gramática CFG. O caminho da gramática e o parser gerado são armazenados como tupla na variável ANALISADORES.
        """
        parser = self.constroi_analisador(sentenca)
        codificada = []
        for t in self.sentenca_anotada:
            if t[1] != "SPT":
                codificada.append(self.remove_acento(t[0]))
        trees = parser.parse_one(codificada)

        return trees

    def constroi_analisador(self, s):
        """Constrói analisador a partir de uma única sentença não anotada, dada como lista de tokens, e uma lista de regras sintáticas no formato CFG, armazenadas em arquivo. Esta função tem um bug, causado pela maneira como o Aelius etiqueta sentenças usando o módulo ProcessaNomesProprios: quando a sentença se inicia por paravra com inicial minúscula, essa palavra não é incorporada ao léxico, mas a versão com inicial maiúscula.
        """
        self.sentenca_anotada = self.etiqueta_sentenca(s)
        self.corrige_anotacao(self.sentenca_anotada)
        entradas = self.gera_entradas_lexicais(self.sentenca_anotada)
        lexico = "\n".join(entradas)
        gramatica = "%s\n%s" % (self.extrai_sintaxe().strip(), lexico)
        cfg = nltk.CFG.fromstring(gramatica)
        return nltk.ChartParser(cfg)

    def remove_acento(self, texto):
        try:
            return unidecode.unidecode(texto)
        except Exception:
            return normalize('NFKD', texto).encode('ASCII', 'ignore').decode()

    def exibe_arvores(self, arvores):
        """Função 'wrapper' para a função de exibição de árvores do NLTK"""
        nltk.draw.draw_trees(*arvores)

    def iniciar_classificacao(self, sentenca):
        tokens = self.toqueniza(sentenca)
        tree = self.analisa_sentenca(tokens)
        return tree, self.sentenca_anotada


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('sentence', help='sentence')
    args, _ = parser.parse_known_args()

    sentence = CharPreprocessing().preprocess(args.sentence)
    print(ClassificaSentencas().iniciar_classificacao(sentence)[1])


if __name__ == '__main__':
    main()
