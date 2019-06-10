# This file is a part of the AnyBlok / Delivery project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
eventCodes = {
    # Colis datant de plus de 90 jours
    'TIMEOUT': 'error',  # code provenant anyblok_delivery

    # Votre colis est prêt à être expédié. Il n'est pas encore pris en charge
    # par La Poste
    "COMCFM": "label",
    # Votre colis est prêt à être expédié. Il n'est pas encore pris en charge
    # par La Poste
    "PCHMQT": "label",
    # Votre colis est pris en charge par La Poste. Il est en cours
    # d'acheminement
    "PCHCFM": "transit",
    # Votre colis est arrivé par erreur sur un site. Il est en cours de
    # réacheminement vers son site de distribution
    "AARDVY": "transit",
    # Votre colis est arrivé sur son site de distribution
    "AARCFM": "transit",
    # Votre colis a été déposé dans un point postal
    "DEPGUI": "delivered",
    # Votre colis est livré
    "LIVCFM": "delivered",
    # Votre colis a été livré au gardien
    "LIVGAR": "delivered",
    # Votre colis a été livré au gardien ou voisin
    "LIVRTI": "delivered",
    # Le colis est livré à l'expéditeur suite à un retour
    "LIVREO": "error",
    # Le destinataire était absent lors de la livraison. Votre colis sera
    # présenté une nouvelle fois le prochain jour ouvré
    "RENNRV": "transit",
    # Votre colis n'a pas pu être distribué par manque d'information. Merci de
    # prendre contact avec notre Service Client via le formulaire disponible
    # sur Internet, afin de fournir les compléments nécessaires
    "RENAIN": "exception",
    # Le colis est retourné à l'expéditeur suite à un refus du destinataire
    "RENAVA": "error",
    # Votre colis est disponible dans votre bureau de poste. Le destinataire
    # dispose de 10 jours ouvrés pour retirer son colis sur présentation de
    # son bon de retrait et d'une pièce d'identité
    "RENAVI": "delivered",
    # Votre colis est disponible dans le point de retrait sélectionné. La date
    # limite de retrait du colis a été précisée au destinataire
    "MLVARS": "delivered",
    # L'adresse de votre colis est incomplète. Nous recherchons la partie non
    # renseignée pour le livrer
    "RENCAD": "exception",
    # Le destinataire du colis n'habite pas à l'adresse indiquée. Le colis est
    # retourné à l'expéditeur
    "RENDIA": "error",
    # Le colis est retourné à l'expéditeur suite à un refus du destinataire
    "RENDIV": "error",
    # Le colis est réexpédié à la demande du destinataire vers l'adresse de
    # son choix
    "RENLNA": "transit",
    # Le colis est retourné à l'expéditeur suite à un refus du destinataire
    "RENSNC": "error",
    # Le colis est retourné à l'expéditeur. Le destinataire a refusé de payer
    # le contre-remboursement
    "RENSRB": "error",
    # Le colis est retourné à l'expéditeur suite à un refus du destinataire
    "RENTAR": "error",
    # Votre colis est disponible au bureau de poste. Le destinataire, une fois
    # l'avis d'instance reçu, dispose de 10 jours ouvrés pour retirer le
    # colis sur présentation d'une pièce d'identité
    "RSTBRT": "delivered",
    # La livraison de votre colis a été reportée pour absence du destinataire
    # ou cas de force majeure
    "RENACP": "transit",
    # Votre colis est en attente de distribution et sera livré prochainement
    "RSTNCG": "transit",
    # Le colis est retourné à l'expéditeur
    "SOLREO": "error",
    # Votre colis est arrivé en France
    "CHGCFM": "transit",
    # Votre colis est arrivé dans le pays de destination
    "DCHCFM": "transit",
    # Votre colis est sorti du bureau d'échange. Il est en cours d'acheminement
    # dans le pays de destination
    "DCHDDT": "transit",
    # Formulaire douanier manquant (DAU), votre colis est retenu en douane.
    # Etude du dossier par la douane
    "DOUAGV": "exception",
    # Certificat d'origine incorrect, votre colis est retenu en douane. Etude
    # du dossier par la douane
    "DOUCOI": "exception",
    # Certificat d'origine manquant, votre colis est retenu en douane. Etude
    # du dossier par la douane
    "DOUCOM": "exception",
    # Certificat d'origine manquant, votre colis est retenu en douane. Etude
    # du dossier par la douane
    "DOUCRR": "exception",
    # Formulaire de déclaration douanière CN23 incorrect, votre colis est
    # retenu en douane. Etude du dossier par la douane
    "DOUDDI": "exception",
    # Formulaire de déclaration douanière CN23 manquant, votre colis est retenu
    # en douane. Etude du dossier par la douane
    "DOUDDM": "exception",
    # Votre colis est retenu en douane pour dédouanement
    "DOUDOU": "exception",
    # Données de virements demandées par la douane, votre colis est retenu en
    # douane
    "DOUDVR": "exception",
    # Vos colis sont retenus en douane. Le nombre de colis ne correspond pas à
    # la déclaration. Etude du dossier par la douane
    "DOUEXI": "exception",
    # Facture incorrecte, votre colis est retenu en douane. Etude du dossier
    # par la douane
    "DOUFCI": "exception",
    # Facture manquante, votre colis est retenu en douane. Etude du dossier par
    # la douane
    "DOUFCM": "exception",
    # Identification du contenu de votre colis en cours, il est retenu en
    # douane
    "DOUIDD": "exception",
    # Informations de dédouanement requises, votre colis est retenu en douane.
    # Etude du dossier par la douane
    "DOUIIR": "exception",
    # En attente du numéro de TVA ou du numéro d'import, votre colis est retenu
    # en douane. Etude du dossier par la douane
    "DOUNIR": "exception",
    # Le contenu de votre colis est prohibé dans le pays de destination, il est
    # retenu en douane. Etude du dossier par la douane
    "DOUPRO": "exception",
    # Licence d'importation requise, votre colis est retenu en douane. Etude du
    # dossier par la douane
    "DOURES": "exception",
    # Votre colis s'apprête à sortir du pays d'origine
    "EXPCFM": "transit",
    # Votre colis est pris en charge par La Poste. Il est en cours
    # d'acheminement
    "PCHCEX": "transit",
    # Le colis est retourné à l'expéditeur
    "SOLREI": "return",
    # "Votre colis n'a pas pu être récupéré car il n'était pas présent dans la
    # boite à lettres. Vous pouvez le déposer en bureau en poste ou chez un
    # commerçant du réseau La Poste."
    "ENEMQT": "exception",
    # Votre colis n'a pu être livré car le destinataire était absent. Il sera
    # remis en livraison le prochain jour ouvré. Le destinataire peut se rendre
    # sur laposte.fr/modification-livraison pour donner de nouvelles
    # instructions.
    'RENARV': 'transit',
    # Votre colis sera présenté le prochain jour ouvré.
    'QDICFM': 'transit',
    # Votre colis va être récupéré dans votre boite aux lettres aujourd'hui.
    'EMLCFM': 'label',
    # Votre colis ne peut être livré ce jour, l'accès à l'adresse de livraison
    # étant impossible. Il sera remis en livraison au plus tôt.
    'RSTFHB': 'exception',
    # Votre colis est livré au voisin indiqué sur l'avis déposé dans la boîte
    # aux lettres du destinataire.
    "LIVVOI": "delivered",
    # Votre colis ne peut être livré ce jour, l'accès à l'adresse de livraison
    # étant impossible. Il sera remis en livraison au plus tôt
    "RSTFMA": "transit",
    # Votre colis a été déposé après l'heure limite de dépôt. Il sera expédié
    # dès le prochain jour ouvré.
    "PCHTAR": "transit",
    # Votre colis sera livré sur rendez-vous à la date choisie par le
    # destinataire.
    "RSTDIL": "transit",
    # Votre colis est en cours de livraison en point de retrait.
    "MLVCFM": "transit",
    # Votre colis a été récupéré dans votre boite aux lettres
    "ECHCFM": 'transit',
    # L'emballage de votre colis a été renforcé pour en assurer sa livraison.
    # Il est en cours d'acheminement.
    "CHGRCA": "exception",
}
