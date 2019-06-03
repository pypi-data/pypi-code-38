# coding=utf-8

import sys
import io

from parapheur.parapheur import config  # Configuration
from parapheur.parapheur import pprint  # Colored printer

req_version = (3, 0)
cur_version = sys.version_info
isp3 = cur_version >= req_version
# pprint.log(cur_version)

if isp3:
    # noinspection PyCompatibility,PyUnresolvedReferences
    import configparser as ConfigParser
else:
    # noinspection PyCompatibility
    import ConfigParser

ALF_CONFIG_PATH = "/opt/iParapheur/tomcat/shared/classes/alfresco-global.properties"

with open(ALF_CONFIG_PATH, 'r') as f:
    config_string = '[Parapheur]\n' + f.read()
config_fp = io.BytesIO(config_string)
config_f = ConfigParser.RawConfigParser()
config_f.readfp(config_fp)

try:
    current_host = config_f.get("Parapheur", "parapheur.hostname")
except ConfigParser.NoOptionError:
    pprint.error("Impossible de récupérer la propriété ", False, '')
    pprint.error("parapheur.hostname", True)

    pprint.info("Vérifier la présence de cette propriété dans le fichier alfresco-global.properties")
    pprint.info("Si celle-ci n'est pas présente, la renseigner avec l'URL ", False, '')
    pprint.warning("ACTUELLE ", True, '')
    pprint.info("(et non la nouvelle)", False)
    exit(1)

new_host = config.get("Parapheur", "new_url")


def replace_hostname_in_file(file_to_handle):
    # Read in the file
    with open(file_to_handle, 'r') as f_read:
        filedata = f_read.read()

    # Replace the target string
    filedata = filedata.replace(current_host, new_host)

    # Write the file out again
    with open(file_to_handle, 'w') as f_write:
        f_write.write(filedata)


# NginX
replace_hostname_in_file("/etc/nginx/conf.d/parapheur.conf")
replace_hostname_in_file("/etc/nginx/conf.d/parapheur_ssl.conf")
# Tomcat
replace_hostname_in_file("/opt/iParapheur/tomcat/scripts/ctl.sh")
replace_hostname_in_file("/opt/iParapheur/tomcat/conf/Catalina/localhost/alfresco.xml")
replace_hostname_in_file("/opt/iParapheur/tomcat/shared/classes/alfresco-global.properties")
replace_hostname_in_file("/opt/iParapheur/tomcat/shared/classes/iparapheur-global.properties")
# WSDL
replace_hostname_in_file("/var/www/parapheur/alfresco/iparapheur.wsdl")

pprint.warning("ATTENTION ! Le certificat serveur configuré dans le fichier /etc/nginx/conf.d/parapheur_ssl.conf "
               "ne correspond potentiellement plus avec le nouveau nom du parapheur.\nIl convient de remplacer "
               "ce certificat (localisé dans le dossier /etc/nginx/ssl/) pour que le parapheur soit totalement "
               "fonctionnel.\n", True)

pprint.success("Propriétés à modifier dans le fichier de configuration /etc/nginx/conf.d/parapheur_ssl.conf :")
pprint.header("- ssl_certficiate /etc/nginx/ssl/certificat.pem;     # Partie publique")
pprint.header("- ssl_certficiate_key /etc/nginx/ssl/certificat.key; # Partie privée\n")

pprint.info("Une fois les modifications de certificat effectuées, relancer le service NginX :")
pprint.header("service nginx restart\n\n")

pprint.success("Modification de nom terminée.")
