#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

import python_ddd

# Ceci n'est qu'un appel de fonction. Mais il est trèèèèèèèèèèès long
# et il comporte beaucoup de paramètres
setup(
    # le nom de votre bibliothèque, tel qu'il apparaitre sur pypi
    name="ddd_es",
    # la version du code
    version=python_ddd.__version__,
    # Liste les packages à insérer dans la distribution
    # plutôt que de le faire à la main, on utilise la foncton
    # find_packages() de setuptools qui va cherche tous les packages
    # python recursivement dans le dossier courant.
    # C'est pour cette raison que l'on a tout mis dans un seul dossier:
    # on peut ainsi utiliser cette fonction facilement
    packages=find_packages(),
    # votre pti nom
    author="Laurent Evrard",
    # Votre email, sachant qu'il sera publique visible, avec tous les risques
    # que ça implique.
    author_email="evrardlaurent77@gmail.com",
    # Une description courte
    description="DDD tools for python",
    # Une description longue, sera affichée pour présenter la lib
    # Généralement on dump le README ici
    long_description=open("README.md").read(),
    # Vous pouvez rajouter une liste de dépendances pour votre lib
    # et même préciser une version. A l'installation, Python essayera de
    # les télécharger et les installer.
    #
    # Ex: ["gunicorn", "docutils >= 0.3", "lxml==0.5a7"]
    #
    # Dans notre cas on en a pas besoin, donc je le commente, mais je le
    # laisse pour que vous sachiez que ça existe car c'est très utile.
    install_requires=["pymongo", "pytest", "pymysql"],
    # Une url qui pointe vers la page officielle de votre lib
    url="https://git.fenrys.io/fenrys/back/python_ddd",
    # Il est d'usage de mettre quelques metadata à propos de sa lib
    # Pour que les robots puissent facilement la classer.
    # La liste des marqueurs autorisées est longue:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    #
    # Il n'y a pas vraiment de règle pour le contenu. Chacun fait un peu
    # comme il le sent. Il y en a qui ne mettent rien.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Communications",
    ],
    # A fournir uniquement si votre licence n'est pas listée dans "classifiers"
    # ce qui est notre cas
    license="WTFPL",
    # Il y a encore une chiée de paramètres possibles, mais avec ça vous
    # couvrez 90% des besoins
)
