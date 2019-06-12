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
import json
import sys

__author__ = 'lhameury'

req_version = (3, 0)
cur_version = sys.version_info
isp3 = cur_version >= req_version


class ParapheurParseType(type):
    def __str__(self):
        toprint = []
        attrs = vars(self)
        for var in attrs.items():
            if "__" not in var[0]:
                toprint.append(var)
        return ', '.join("%s: %s" % item for item in toprint).encode('utf-8')

    def __getitem__(self, key):
        attrs = vars(self)
        for item in attrs.items():
            if key == item[0]:
                return item[1]
        return ""

    def __iter__(self):
        for each in self.__dict__.keys():
            if each[:2] != '__':
                yield self.__getitem__(each)

    def iterkeys(self):
        for each in self.__dict__.keys():
            if each[:2] != '__':
                yield each

    def items(self):
        return [(key, self.__getitem__(key)) for key in self.iterkeys()]

    def copy(self):
        return dict((k, v) for k, v in self.items())


# JSON Helper
def json_to_obj(s):
    def h2o(x):
        if isinstance(x, dict):
            n = {}
            if isp3:
                for k, v in x.items():
                    n[k] = h2o(v)
            else:
                # noinspection PyCompatibility
                for k, v in x.iteritems():
                    n[k] = h2o(v)
            return ParapheurParseType('jo', (), n)
        if isinstance(x, list):
            element = []
            for v in x:
                element.append(h2o(v))
            return element
        if isinstance(x, str) or isinstance(x, unicode):
            return x.encode('utf-8')
        else:
            return x

    return h2o(json.loads(s))
