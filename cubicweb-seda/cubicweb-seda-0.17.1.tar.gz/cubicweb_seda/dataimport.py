# coding: utf-8
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-seda data import tools"""

from __future__ import print_function

from itertools import count
from os.path import abspath, dirname, join

from six import text_type

from cubicweb.server.checkintegrity import reindex_entities
from cubicweb.dataimport.stores import NoHookRQLObjectStore
from cubicweb.dataimport.importer import (
    SimpleImportLog,
    cwuri2eid,
)

from cubicweb_skos import lcsv, sobjects as skos

# If you want to add a vocabulary here, add it to the end of the list if you
# want to create it in migration script by simply calling import_seda_schemes
# for proper interaction with saem which attempt to allocate reproducible ARK
# identifier to them.
LCSV_FILES = [(title, rtype, etype,
               join(abspath(dirname(__file__)), 'migration', 'data', fname))
              for title, rtype, etype, fname in (
    # schemes extracted from SEDA 2 XSD
    (u'SEDA 2 : Actions',
     'seda_final_action', 'SEDAStorageRule',
     'final_action_storage_code_type.csv'),
    (u'SEDA 2 : Unités de mesure',
     'seda_unit', ('SEDAWidth', 'SEDAHeight', 'SEDADepth',
                   'SEDADiameter', 'SEDALength', 'SEDAThickness'),
     'measurement_units_type.csv'),
    (u'SEDA 2 : Unités de poids',
     'seda_unit', 'SEDAWeight',
     'measurement_weight_units_type.csv'),
    (u'SEDA : Types de mot-clé',
     'seda_keyword_type_to', (),
     'code_keyword_type.csv'),
    (u'SEDA 2 : Status légaux',
     'seda_legal_status_to', (),
     'legal_status.csv'),
    (u'SEDA : Niveaux de description',
     'seda_description_level', (),
     'level_type.csv'),
    # schemes extracted from SEDA 2 XSD, completed to support earlier SEDA versions
    (u'SEDA : Sort final',
     'seda_final_action', 'SEDAAppraisalRule',
     'final_action_appraisal_code_type.csv'),
    # schemes extracted from earlier SEDA versions
    (u"SEDA : Durée d'utilité administrative",
     'seda_rule', 'SEDASeqAppraisalRuleRule',
     'dua.csv'),
    (u"SEDA : Codes de restriction d'accès",
     'seda_rule', 'SEDASeqAccessRuleRule',
     'access_control.csv'),
    (u"SEDA : Règles de diffusion",
     'seda_rule', 'SEDASeqDisseminationRuleRule',
     'dissemination.csv'),
    (u"SEDA : Types d'objets-données",
     'seda_type_to', (),
     'document_type_code.csv'),
    # other schemes
    (u'Types MIME',
     'seda_mime_type_to', (),
     'mime_types.csv'),
    (u"Types d'évènement",
     'seda_event_type_to', (),
     'event_types.csv'),
    (u'Encodages (extraits du schéma UN/CEFACT)',
     'seda_encoding_to', (),
     'encodings.csv'),
    (u'Formats de fichier (PRONOM)',
     'seda_format_id_to', (),
     'file_formats.csv'),
    (u'Niveau de classification (IGI 1300)',
     'seda_classification_level', (),
     'classification_levels.csv'),
    (u'Langues (ISO-639-3)',
     (), (),
     'languages.csv'),
    (u"Algorithmes d'empreinte",
     'seda_algorithm', 'SEDABinaryDataObject',
     'digest_algorithms.csv'),

    (u'Catégories de fichier',
     'file_category', (),
     'file_categories.csv'),
    (u'Langues restreintes (compatible SEDA 0.2)',
     ('seda_language_to', 'seda_description_language_to'), (),
     'languages-seda02.csv'),
)]


def lcsv_import(cnx, store, fname, scheme_uri, **kwargs):
    """Actually import LCSV data file."""
    with open(fname) as stream:
        extentities = skos.lcsv_extentities(stream, scheme_uri, ';', 'utf-8')
        import_log = SimpleImportLog(fname)
        skos.store_skos_extentities(cnx, store, extentities, import_log,
                                    raise_on_error=True, extid_as_cwuri=False, **kwargs)


def lcsv_check(cnx, store, fname, scheme_uri, separator=';', **kwargs):
    """Simply check data file consistency."""
    counter = count()

    def uri_generator(val):
        return text_type(next(counter)) + val

    with open(join(dirname(__file__), 'migration', 'data', fname)) as stream:
        lcsv2rdf = lcsv.LCSV2RDF(stream, separator, 'utf-8',
                                 # XXX drop once skos is released
                                 uri_generator=uri_generator, uri_cls=text_type)
        list(lcsv2rdf.triples())

        # also check there are the expected number of separator for each line
        stream.seek(0)
        expected_separators = stream.readline().count(separator)
        for i, line in enumerate(stream):
            if line.count(separator) != expected_separators:
                linenum = i + 2
                raise AssertionError('Got %s %s on line %s of %s, %s where expected'
                                     % (line.count(separator), separator, linenum,
                                        fname, expected_separators))


def init_seda_scheme(cnx, title):
    """Create a scheme to hold SEDA concepts with the given title.

    Separated function to be monkey-patched if one need to customize the store (eg saem).
    """
    description = u'edition 2009' if title.startswith('SEDA :') else None
    return cnx.create_entity('ConceptScheme', title=title, description=description)


def get_store(cnx):
    """Return the store to be used to import LCSV data files.

    Separated function to be monkey-patched if one needs to customize the store (eg saem).
    """
    if cnx.repo.system_source.dbdriver == 'postgres':
        from cubicweb.dataimport.massive_store import MassiveObjectStore
        return MassiveObjectStore(cnx, eids_seq_range=1000)
    else:
        return NoHookRQLObjectStore(cnx)


def import_seda_schemes(cnx, lcsv_import=lcsv_import, lcsv_files=LCSV_FILES):
    """Import all LCSV data files defined in LCSV_FILES."""
    extid2eid = cwuri2eid(cnx, ('ConceptScheme', 'Label'))
    # concepts and external URIs may come from any source
    extid2eid.update(cwuri2eid(cnx, ('Concept', 'ExternalUri')))
    store = get_store(cnx)
    for title, rtypes, etypes, fname in lcsv_files:
        if not cnx.find('ConceptScheme', title=title):
            print('importing', title.encode('utf-8'))
            scheme = init_seda_scheme(cnx, title)
            extid2eid[scheme.cwuri] = scheme.eid
            lcsv_import(cnx, store, fname, scheme.cwuri, extid2eid=extid2eid)
            if not isinstance(rtypes, tuple):
                rtypes = (rtypes,)
            for rtype in rtypes:
                rtype_e = cnx.find('CWRType', name=rtype).one()
                scheme.cw_set(scheme_relation_type=rtype_e)
            if not isinstance(etypes, tuple):
                etypes = (etypes,)
            for etype in etypes:
                etype_e = cnx.find('CWEType', name=etype).one()
                scheme.cw_set(scheme_entity_type=etype_e)
            store.flush()
    store.commit()
    store.finish()
    if not isinstance(store, NoHookRQLObjectStore):
        # when using the massive store, we need explicit reindexation
        reindex_entities(cnx.repo.schema, cnx, etypes=['Concept', 'ConceptScheme'])
