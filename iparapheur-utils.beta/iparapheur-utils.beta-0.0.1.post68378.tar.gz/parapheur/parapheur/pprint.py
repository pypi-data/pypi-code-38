# coding=utf-8
# module Parapheur
"""
CeCILL Copyright (c) 2006-2015, ADULLACT-projet
Initiated by ADULLACT-projet S.A.
Developped by ADULLACT-projet S.A.

contact@adullact-projet.coop

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant
donné sa spécificité de logiciel libre, qui peut le rendre complexe à
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement,
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.
"""
from __future__ import print_function

import time

__author__ = 'lhameury'


def __init__():
    pass


def log_to_file(enable_log):
    global __log_to_file__
    __log_to_file__ = enable_log


def cstr(v):
    if isinstance(v, str):
        try:
            return v.encode('utf-8')
        except UnicodeDecodeError:
            return v
    return str(v)


def do_log(tolog, bold, end, type, color):
    if __log_to_file__:
        with open(__log_file__, 'a') as f:
            date = time.strftime("%d/%m/%Y %H:%M:%S")
            print("{0}  {1}  {2}".format(date, type, tolog), file=f)
    else:
        print(color + ("", __BOLD__)[bold] + cstr(tolog) + __ENDC__, end=end)


def log(tolog, bold=False, end='\n'):
    do_log(tolog, bold, end, "LOG", "")


def header(tolog, bold=False, end='\n'):
    do_log(tolog, bold, end, "HEADER", __HEADER__)


def info(tolog, bold=False, end='\n'):
    do_log(tolog, bold, end, "INFO", __OKBLUE__)


def success(tolog, bold=False, end='\n'):
    do_log(tolog, bold, end, "SUCCESS", __OKGREEN__)


def warning(tolog, bold=False, end='\n'):
    do_log(tolog, bold, end, "WARNING", __WARNING__)


def error(tolog, bold=True, end='\n'):
    do_log(tolog, bold, end, "ERROR", __FAIL__)

__log_to_file__ = False
# Set filename and clear it
__log_file__ = "iparapheur-utils.log"
open(__log_file__, 'w').close()

__HEADER__ = '\033[95m'
__OKBLUE__ = '\033[94m'
__OKGREEN__ = '\033[92m'
__WARNING__ = '\033[93m'
__FAIL__ = '\033[91m'
__ENDC__ = '\033[0m'
__BOLD__ = '\033[1m'
__UNDERLINE__ = '\033[4m'
