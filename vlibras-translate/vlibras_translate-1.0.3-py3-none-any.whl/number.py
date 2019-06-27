################################################################
# LAViD - Laboratório de Aplicações de Vídeo Digital
################################################################
# Autor: Caio Moraes
# Email: caiomoraes.cesar@gmail.com
# GitHub: MoraesCaio
#
# LEMBRETE: Essa classes é muito sensível a reordenação
#            de linhas!
################################################################


from .ConverteExtenso import convert_extenso, roman_to_int
from .Iterator import Iterator
import argparse
from unidecode import unidecode
from collections import deque
import re
from .dExtenso import dExtenso


class Number:

    acceptable = [
        'zero', 'um', 'dois', 'tres', 'quatro', 'cinco', 'seis', 'sete',
        'oito', 'nove', 'dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze',
        'dezesseis', 'dezessete', 'dezoito', 'dezenove', 'vinte', 'trinta',
        'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa',
        'cento', 'cem', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos',
        'seiscentos', 'setecentos', 'oitocentos', 'novecentos', 'mil',
        'milhao', 'milhoes', 'bilhao', 'bilhoes', 'trilhao', 'trilhoes',
        'catorze', 'cincoenta', 'uma', 'duas'
    ]

    ordinais = [
        'zerésimo', 'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
        'sexto', 'sétimo', 'oitavo', 'nono'
    ]

    extenso = dExtenso()

    def set_ord(self, lista):

        for postag in lista:

            if re.fullmatch(r'\d+[ªº]', postag[0]):
                postag[0] = postag[0].replace('ª', 'º')
                postag[1] = 'ORD'
            else:
                postag[0] = postag[0].replace('º', '').replace('ª', '')

        return lista

    def to_ord_Libras(self, lista):

        for postag in lista:
            if postag[1] == 'ORD':
                postag[0] = postag[0].replace('º', '').replace('ª', '')

                try:
                    new_token = ''
                    for c in postag[0]:
                        new_token += self.ordinais[int(c)] + ' '
                    postag[0] = new_token[:-1]
                except Exception as e:
                    pass

        return lista

    def to_extenso(self, lista):
        for postag in lista:
            if postag[1].startswith('NUM'):
                if '.' in postag[0]:
                    integers, decimals = postag[0].split('.')
                    ext_integers = self.extenso.getExtenso(integers)
                    ext_decimals = self.extenso.getExtenso(decimals)
                    postag[0] = (ext_integers + '.' + ext_decimals).replace(' e', ' ')
                else:
                    postag[0] = self.extenso.getExtenso(postag[0])

        return lista

    def converter_extenso(self, lista):
        '''Converte número por extenso para sua forma numerica.
        '''
        lista_extensos = []
        indices_deletar = []
        count = 0
        is_sequence = False
        for i in range(len(lista)):
            token = lista[i][0]
            tag = lista[i][1]
            if tag.startswith("NUM") and token.isalpha() or\
                    (is_sequence and tag.startswith('D-UM') and not tag.endswith('-P')):
                # Verifico se não há sequência de obtenção de extenso em andamento para começar a obter um nova sequência
                # print('True' if is_sequence else 'False')
                if not is_sequence:  # and len(lista_extensos) == count (???)
                    lista_extensos.append([i, [token]])  # i = Posição do primeiro extenso encontrado, token = número por extenso
                    is_sequence = True
                else:
                    lista_extensos[count][1].append(token)  # Pego número por extenso que está na sequência e adiciona na lista
                    # print('indices_deletar.append(i)')
                    indices_deletar.append(i)  # Insiro indice na lista para ser removido depois
            elif is_sequence:
                # Se o token anterior e o próximo foram classificados como número, e o token atual como conjunção, significa que podemos remove-lo
                if ((i + 1 < len(lista)) and (lista[i - 1][1] == "NUM") and (lista[i + 1][1] == "NUM" or lista[i + 1][1].startswith("D-UM")) and (tag == "CONJ")):
                    indices_deletar.append(i)
                else:
                    # A sequência foi quebrada, o que significa que selecionamos o extenso do número por completo
                    # Podemos agora procurar por outra sequencia de número por extenso na lista
                    is_sequence = False
                    count += 1

        for extenso in lista_extensos:
            soma = convert_extenso(' '.join(extenso[1]))

            lista[extenso[0]] = [str(soma), "NUM"]

        deque((list.pop(lista, i) for i in sorted(indices_deletar, reverse=True)), maxlen=0)
        return lista

    def simplificar_sentenca(self, lista, cardinal=True):
        '''Simplifica a sentença para que possa evitar a ditalogia.
        Como por exemplo a troca de uma palavra no plural para singular.
        '''
        lista_simplificada = list(lista)
        it = Iterator()
        it.load(lista_simplificada)

        while(it.has_next()):

            try:
                num_romano = roman_to_int(it.get_word())
                if it.get_prev_ticket()[-2:] == "-F":
                    lista_simplificada[it.get_count()] = [num_romano + "ª", 'ORD']
                else:
                    lista_simplificada[it.get_count()] = [num_romano + "º", 'ORD']
            except:
                pass

        lista_simplificada = self.set_ord(lista_simplificada)

        if cardinal:
            try:
                lista_simplificada = self.converter_extenso(lista_simplificada)
            except:
                pass
        else:
            lista_simplificada = self.to_extenso(lista_simplificada)

        return lista_simplificada


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('extenso', help='Número por extenso')
    args, _ = parser.parse_known_args()

    n = Number()

    exs = unidecode(args.extenso.lower()).split()
    extensos = [e for e in exs if e in n.acceptable]
    print('result', convert_extenso(' '.join(extensos)))


if __name__ == '__main__':
    main()
