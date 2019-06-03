#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
from datetime import datetime, timedelta

from progress.bar import IncrementalBar

import parapheur  # Configuration
from parapheur.parapheur import config
from parapheur.parapheur import pprint  # Colored printer

__config_section__ = "RecupArchives"

# Init REST API client
client = parapheur.getrestclient()

# Params
recup_folder = config.get(__config_section__, "folder")
# recup_folder = "/tmp/getdoc/"
page_size = config.get(__config_section__, "page_size")
# page_size = "500"

use_only_print_pdfs = config.get(__config_section__, "use_only_print_pdfs") == "true"
# use_only_print_pdfs = False
use_reduced_download_path = config.get(__config_section__, "use_reduced_download_path") == "true"
# use_reduced_download_path = False
purge = config.get(__config_section__, "purge") == "true"
# purge = False
download = config.get(__config_section__, "download") == "true"
# download = True

type_filter = config.get(__config_section__, "type_filter")
# type_filter = "*"
subtype_filter = config.get(__config_section__, "subtype_filter")
# subtype_filter = "*"
waiting_days = int(config.get(__config_section__, "waiting_days"))
# waiting_days = 0


# region Private methods


def move_incomplete_download_to_temp(path):
    temp_version = 1
    while os.path.exists("{0}_temp{1}".format(path, temp_version)):
        temp_version += 1
    os.rename("{0}".format(path), "{0}_temp{1}".format(path, temp_version))


def get_reduced_folder_path(dossier_type, dossier_subtype, dossier_title, dossier_id):
    """
    {rootFolder}/{Type}/{DossierName}/
    Possibly with a " (2)" suffix, if a folder with the same name already exists.

    This folder will be created with an empty Subtitle and NodeId file,
    to avoid any lost information.
    :return: download absolute path, or None if already exists
    """
    base_folder = "{0}/{1}".format(recup_folder, dossier_type)
    reduced_path = "{0}/{1}".format(base_folder, dossier_title)

    is_same_id = os.path.exists("{0}/.{1}".format(reduced_path, dossier_id))
    if is_same_id:
        return reduced_path

    if os.path.exists(reduced_path):
        version = 2

        while os.path.exists("{0} ({1})".format(reduced_path, version)):
            versioned_path = "{0} ({1})".format(reduced_path, version)

            is_same_id = os.path.exists("{0}/.{1}".format(versioned_path, dossier_id))
            if is_same_id:
                return versioned_path

            version += 1
        reduced_path = "{0} ({1})".format(reduced_path, version)

    os.makedirs(reduced_path, 0755)
    os.mknod("{0}/.{1}".format(reduced_path, dossier_id))
    os.mknod("{0}/.{1}".format(reduced_path, dossier_subtype))
    return reduced_path


def get_full_folder_path(dossier_type, dossier_subtype, dossier_title, dossier_id):
    """
    {rootFolder}/{Type}/{SubType}{DossierName}_{DossierId}/
    :return: download absolute path, or None if already exists
    """
    full_path = "{0}/{1}/{2}/{3}_{4}".format(recup_folder, dossier_type, dossier_subtype, dossier_title, dossier_id)

    if not os.path.exists(full_path):
        os.makedirs(full_path, 0755)

    return full_path


def cleanup_special_chars(string):
    # Windows Forbidden punctuation
    cleaned = re.sub(u"<", "(", string)
    cleaned = re.sub(u">", ")", cleaned)
    cleaned = re.sub(u":", "=", cleaned)
    cleaned = re.sub(u"\"", "''", cleaned)
    cleaned = re.sub(u"[\\/\|]", "-", cleaned)
    cleaned = re.sub(u"\n", " ", cleaned)
    cleaned = re.sub(u"[\*\?%€&£$§#°]", "_", cleaned)

    # Special chars
    cleaned = re.sub(u'[ÀÁÂÄ]', 'A', cleaned)
    cleaned = re.sub(u'[ÈÉÊË]', 'E', cleaned)
    cleaned = re.sub(u'[ÍÌÎÏ]', 'I', cleaned)
    cleaned = re.sub(u'[ÒÓÔÖ]', 'O', cleaned)
    cleaned = re.sub(u'[ÙÚÛÜ]', 'U', cleaned)
    cleaned = re.sub(u'[áàâä]', 'a', cleaned)
    cleaned = re.sub(u'[éèêë]', 'e', cleaned)
    cleaned = re.sub(u'[íìîï]', 'i', cleaned)
    cleaned = re.sub(u'[óòôö]', 'o', cleaned)
    cleaned = re.sub(u'[úùûü]', 'u', cleaned)
    cleaned = re.sub(u'Æ', 'AE', cleaned)
    cleaned = re.sub(u'æ', 'ae', cleaned)
    cleaned = re.sub(u'Œ', 'OE', cleaned)
    cleaned = re.sub(u'œ', 'oe', cleaned)
    cleaned = re.sub(u'Ç', 'C', cleaned)
    cleaned = re.sub(u'ç', 'c', cleaned)

    # Fix for Lille Metropole and Ville Lille
    # cleaned = re.sub(r'[^\w\d\.\-_\(\)]', '_', cleaned)

    cleaned = cleaned.replace(u'\xb0', ".")
    cleaned = cleaned.replace(u'\xa0', ".")
    cleaned = cleaned.replace(u'\xab', ".")
    cleaned = cleaned.replace(u'\xbb', ".")
    cleaned = cleaned.replace(u'\xb2', "2")
    cleaned = cleaned.replace(u'\xe7', "c")
    cleaned = cleaned.replace(u'\xe8', "e")
    cleaned = cleaned.replace(u'\xe9', "e")
    cleaned = cleaned.replace(u'\xea', "e")
    cleaned = cleaned.replace(u'\u2013', "-")
    cleaned = cleaned.replace(u'\u2018', "'")
    cleaned = cleaned.replace(u'\u2019', "'")
    cleaned = cleaned.replace(u'\u0009', " ")

    if len(cleaned) == 0:
        cleaned = "dossier_sans_nom"

    # Cas du fs ext4 - réduction du nombre de caractère à 200 (titre + id ~ 250)
    cleaned = cleaned[0:200]

    return cleaned


# endregion


type_filter = type_filter.replace(" ", "%20")
subtype_filter = subtype_filter.replace(" ", "%20")
download_folder_path = None

if client.islogged:

    # Fetch folders

    # Get maxdate for filtering. -1 because we don't count today as a day !
    newdate = datetime.today() - timedelta(days=waiting_days - 1)
    datefilterstr = "%s-%s-%s" % (newdate.year, '%02d' % newdate.month, '%02d' % newdate.day)

    page = 0
    dossiers_archive = []

    dossiers_fetched = [1]
    while len(dossiers_fetched) > 0:
        dossiers_fetched = client.doget(
            "/parapheur/archives",
            dict(
                page=str(page),
                filter='{"and":[{"or":[{"ph:typeMetier":"%s"}]},{"or":[{"ph:soustypeMetier":"%s"}]}]}' % (
                        type_filter, subtype_filter),
                pageSize=page_size
            )
        )
        if dossiers_fetched is not False:
            dossiers_archive += dossiers_fetched
            pprint.log("Page {0} : {1} dossiers".format(page, len(dossiers_fetched)))
        else:
            pprint.error("Page {0} : Erreur de récupération".format(page))
            dossiers_fetched = [1]
        page += 1

    pprint.log("{0} dossier(s) trouvé(s)".format(len(dossiers_archive)))

    # Waiting delay

    if waiting_days > 0:
        timestamp = (int(time.time()) - 60 * 60 * 24 * waiting_days) * 1000
        dossiers_archive = [d for d in dossiers_archive if d['created'] < timestamp]
        pprint.log("{0} dossier(s) apres le delai de carence".format(len(dossiers_archive)))

    bar = IncrementalBar('Recuperation des archives', max=len(dossiers_archive), suffix='%(index)d/%(max)d - %(eta)ds')

    # Download

    for dossier_index in range(0, len(dossiers_archive)):

        dossier = dossiers_archive[dossier_index]
        title_clean = cleanup_special_chars(dossier['title'])
        type_clean = cleanup_special_chars(dossier['type'])
        subtype_clean = cleanup_special_chars(dossier['sousType'])

        if download:

            # Create folders

            if use_only_print_pdfs:
                download_folder_path = recup_folder
            else:
                if use_reduced_download_path:
                    download_folder_path = get_reduced_folder_path(type_clean, subtype_clean, title_clean, dossier['id'])
                else:
                    download_folder_path = get_full_folder_path(type_clean, subtype_clean, title_clean, dossier['id'])

            # Cleanup

            is_already_downloaded = os.path.exists("{0}/.done".format(download_folder_path))

            if use_reduced_download_path:
                folder_already_contains_data = len(os.listdir(download_folder_path)) > 2
            else:
                folder_already_contains_data = len(os.listdir(download_folder_path)) > 0

            if folder_already_contains_data and not is_already_downloaded and not use_only_print_pdfs:
                move_incomplete_download_to_temp(download_folder_path)

                if use_reduced_download_path:
                    download_folder_path = get_reduced_folder_path(type_clean, subtype_clean, title_clean,
                                                                   dossier['id'])
                else:
                    download_folder_path = get_full_folder_path(type_clean, subtype_clean, title_clean, dossier['id'])

            # Download content

            if not is_already_downloaded and not use_only_print_pdfs:

                content_url = "/api/node/content/workspace/SpacesStore/{0}/{1}".format(dossier['id'], title_clean)
                content_url = content_url.replace(" ", "%20")
                client.dodownload(content_url, "{0}/{1}".format(download_folder_path, title_clean))

                if dossier['original'] == "true":

                    if dossier['isXemEnabled']:
                        dossier_distant_original_name = title_clean
                        dossier_local_original_name = "{0}_original.xml".format(title_clean)
                    elif hasattr(dossier, 'originalName') and dossier['originalName'] is not None:
                        dossier_distant_original_name = cleanup_special_chars(dossier['originalName'])
                        dossier_local_original_name = "original_" + dossier_distant_original_name
                    else:
                        dossier_distant_original_name = title_clean
                        dossier_local_original_name = "original_" + title_clean

                    original_url = "/api/node/content%3bph%3aoriginal/workspace/SpacesStore/{0}/{1}".format(
                        dossier['id'], dossier_distant_original_name)
                    original_url = original_url.replace(" ", "%20")
                    client.dodownload(original_url, "{0}/{1}".format(download_folder_path, dossier_local_original_name))

                if dossier['sig'] == "true":
                    sign_url = "/api/node/content%3bph%3asig/workspace/SpacesStore/{0}/{1}_sig.zip".format(
                        dossier['id'], title_clean)
                    sign_url = sign_url.replace(" ", "%20")
                    client.dodownload(sign_url, "{0}/{1}_sig.zip".format(download_folder_path, title_clean))

                os.mknod("{0}/.done".format(download_folder_path))
                # pprint.success("Downloaded : {0} ({1}/{2})".format(dossier['id'], dossier_index + 1, len(dossiers_archive)))
            else:
                if not use_only_print_pdfs:
                    pprint.warning("Already downloaded : {0} ({1}/{2})".format(dossier['id'], dossier_index + 1,
                                                                               len(dossiers_archive)))

            # very special thing (only print-PDF files, flat-stored. sogecap-style)

            if use_only_print_pdfs:
                content_url = "/api/node/content/workspace/SpacesStore/{0}/{1}".format(dossier['id'], title_clean)
                content_url = content_url.replace(" ", "%20")
                client.dodownload(content_url, "{0}/{1}".format(download_folder_path, title_clean))


        if purge:
            if download:
                if os.path.exists("{0}/.done".format(download_folder_path)) or use_only_print_pdfs:
                    client.executescript("removeNode.js", format=(dossier['id'],))
            else:
                client.executescript("removeNode.js", format=(dossier['id'],))
                #  pprint.success("Deleted : {0} ({1}/{2})".format(dossier['id'], dossier_index + 1, len(dossiers_archive)))

        bar.next()

    bar.finish()

pprint.success("Done", True)
