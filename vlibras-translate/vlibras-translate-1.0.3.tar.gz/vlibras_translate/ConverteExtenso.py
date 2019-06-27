#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################
# LAViD - Laboratório de Aplicações de Vídeo Digital
################################################################
# Autor: Caio Moraes
# Email: caiomoraes.cesar@gmail.com
# GitHub: MoraesCaio
#
# Ajuste:
#   uso de unidecode no lugar de normalize para python 3
# Correções:
#   seissentos -> seiscentos
#   setessentos -> setecentos
# Adições:
#   uma, duas, catorze, cincoenta
################################################################
# Autor: Erickson Silva
# Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>
################################################################

import argparse
from unicodedata import normalize
from unidecode import unidecode
from .Iterator import *
import re

num = {"zero": 0, "um": 1, "dois": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6,
       "sete": 7, "oito": 8, "nove": 9, "uma": 1, "duas": 2}

ext = [{"um": "1", "dois": "2", "tres": "3", "quatro": "4", "cinco": "5", "seis": "6",
        "sete": "7", "oito": "8", "nove": "9", "dez": "10", "onze": "11", "doze": "12",
        "treze": "13", "quatorze": "14", "quinze": "15", "dezesseis": "16",
        "dezessete": "17", "dezoito": "18", "dezenove": "19", "catorze": "14",
        "uma": "1", "duas": "2"},
       {"vinte": "2", "trinta": "3",
        "quarenta": "4", "cinquenta": "5", "sessenta": "6", "setenta": "7", "oitenta": "8",
        "noventa": "9", "cincoenta": "5"},
       {"cento": "1", "cem": "1", "duzentos": "2", "trezentos": "3",
        "quatrocentos": "4", "quinhentos": "5", "seiscentos": "6", "setecentos": "7",
        "oitocentos": "8", "novecentos": "9"}]

und = {"mil": 1000, "milhao": 1000000, "bilhao": 1000000000, "trilhao": 1000000000000}
unds = {"mil": "000", "milhao": "000000", "milhoes": "000000", "bilhao": "000000000", "bilhoes": "000000000", "trilhao": "000000000000", "trilhoes": "000000000000"}


def int_to_roman(input):
    if not isinstance(input, type(1)):
        raise TypeError("expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = []

    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    return ''.join(result)


def roman_to_int(input):
    if not isinstance(input, type("")):
        raise TypeError("expected string, got %s" % type(input))

    if not re.match(r'[MDCLXVI]+', input):
        raise ValueError('input is not a valid Roman numeral')

    nums = {'M': 1000,
            'D': 500,
            'C': 100,
            'L': 50,
            'X': 10,
            'V': 5,
            'I': 1}
    sum = 0
    for i in range(len(input)):
        try:
            value = nums[input[i]]
            if i + 1 < len(input) and nums[input[i + 1]] > value:
                sum -= value
            else:
                sum += value
        except KeyError:
            raise ValueError('input is not a valid Roman numeral: %s' % input)

    if int_to_roman(sum) == input:
        return str(sum)
    else:
        raise ValueError('input is not a valid Roman numeral: %s' % input)


def oneDigit(x):
    return ext[0][x]


def twoDigit(x):
    try:
        return ext[1][x[0]] + ext[0][x[1]]
    except:
        return ext[1][x[0]] + "0"


def threeDigit(x):
    return ext[2][x[0]] + ext[1][x[1]] + ext[0][x[2]]

# Erickson: Não faço mais a minima idéia de como fiz isso, só sei que funciona!


def extensoUnit(n):
    sn = n.split(",")
    size = len(sn)
    firstWord = sn[0]
    endWord = ""
    numExt = ""

    if(sn[size - 1] in unds):
        size -= 1
        endWord = sn[size]
        del sn[size]

    if(firstWord in ext[0]):
        numExt = oneDigit(firstWord)

    elif (firstWord in ext[1]):
        numExt = twoDigit(sn)

    elif (firstWord in ext[2]):
        if(size == 1):
            numExt = ext[2][firstWord] + "00"
        elif (size == 2):
            if(sn[1] == "dez"):
                numExt = ext[2][firstWord] + oneDigit(sn[1])
            try:
                numExt = ext[2][firstWord] + "0" + oneDigit(sn[1])
            except:
                numExt = ext[2][firstWord] + twoDigit([sn[1]])
        else:
            numExt = threeDigit(sn)

    if(endWord != ""):
        numExt = numExt + unds[endWord]

    return numExt


'''
Comece com uma lista vazia. Itere pelas palavras da string da esquerda
para direita. Ao encontrar um numeral, adicione o número à lista se a
última palavra foi uma escala, ou some ao último numero da lista se a
última palavra foi um numeral. Ao encontrar uma escala, multiplique o
último número da lista de acordo. Quando terminar, some tudo e retorne
o resultado.
'''

# TODO: Refatorar para nao usar mais o extensoUnit


def convert_extenso(extenso):
    global newToken, auxToken
    extensoQuebrado = extenso.lower().split(" ")

    # print(f'extensoQuebrado {extensoQuebrado}')
    if len(extensoQuebrado) == 1 and simplifica(extensoQuebrado[0]) in und:
        return extenso
    nums = []
    it = Iterator()
    it.load(extensoQuebrado)
    while(it.has_next()):
        token = simplifica(it.get_token())
        tokenAnterior = simplifica(it.get_token(-1))
        if (token in und):
            if(it.get_count() == 0):
                nums.append(und[token])
            else:
                newToken = und[token] * int(nums[-1])
                nums[-1] = newToken
        else:
            if (token in num):
                auxToken = num[token]
            elif (token not in und):
                auxToken = extensoUnit(token)

            if((tokenAnterior not in und) and it.get_count() > 0):
                # print(f'auxToken {auxToken}')
                # print(f'nums[-1] .{type(nums[-1])}.')

                newToken = int(auxToken) + int(nums[-1])
                nums[-1] = newToken
            else:
                nums.append(auxToken)
    return soma(nums)


def soma(lista):
    soma = 0
    for i in lista:
        try:
            soma += int(i)
        except:
            continue
    return soma


def simplifica(txt):
    newToken = ""

    try:
        newToken = unidecode(txt)
    except:
        newToken = normalize('NFKD', txt.encode('iso-8859-1').decode('iso-8859-1')).encode('ASCII', 'ignore')

    if(newToken[-3:] == "oes"):
        return newToken[:-3] + "ao"

    return newToken


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('extenso', help='Número por extenso')
    args, _ = parser.parse_known_args()

    exs = unidecode(args.extenso.lower()).split()

    acceptable = ['zero']
    [acceptable.extend(list(i.keys())) for i in [ext[0], ext[1], ext[2], unds]]

    extensos = [e for e in exs if e in acceptable]

    # print(convert_extenso(' '.join(extensos)))


if __name__ == '__main__':
    main()
