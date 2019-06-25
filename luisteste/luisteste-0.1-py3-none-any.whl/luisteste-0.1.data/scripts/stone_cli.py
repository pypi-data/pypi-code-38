#!/usr/bin/python3

#from Modulo.Arquivo import something
import sys
from Modulos.Azure import Azure
from Modulos.GCP import GCP
from Modulos.Cloud import Cloud


def usage():
    print("""
        Bla bla bla usage""")

def switch(x):
    az = Azure()
    gcp = GCP()
    funcoes = {
        "-gcp":gcp.criar_vm,
        "-az":az.criar_vm,
        "-h":usage
    }

    try:
        return funcoes[x]
    except Exception as e:
        print("Argumento não mapeado",e)

try:
    switch(sys.argv[1])()
except Exception as e:
    if len(sys.argv)==1:
        print("0 numero de argumentos eh invalido")
