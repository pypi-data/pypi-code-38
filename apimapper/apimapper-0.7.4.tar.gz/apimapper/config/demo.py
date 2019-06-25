from config.config import *
## Example configurations

# MAPPING
'''
{  RESULT: top level field containing the result (can be omitted. useful when the externam API response is contained inside value of a field)
   FILTER: {from-field-1: expected-value1, ...}, # only results containing "expected-value" in the from-field for all the items in this dict will be returned. 
   DIRECT: {to-field (wrapped response): from-field (external api response)}, # when a field is directly mapped - put it here
   RULES: {to-field: {RULE: any simple string rule for eval - enclose parameter containing in "{}",
                      FIELDS: {parametername: fieldname}}}
 }
'''


GND_PERSON_MAP = {DIRECT: {'label': 'label',
                           'uri': 'id'},
                  RULES: {'source': {RULE: '"GND"'},
                          'label_name': {RULE: '"{p1}".split("|")[0].strip()',
                                         FIELDS: {'p1': 'label'}},
                          'label_year': {RULE: '"{p1}".split("|")[1].strip() if "{p1}".split("|")[1].strip()[0].isnumeric() else ""',
                                         FIELDS: {'p1': 'label'}},
                          'label_profession': {RULE: '"{p1}".split("|")[2].strip() if "{p1}".split("|")[1].strip()[0].isnumeric() else "{p1}".split("|")[1].strip()',
                                               FIELDS: {'p1': 'label'}}}}
           
VIAF_PERSON_MAP = {RESULT: 'result',
                   FILTER: {'nametype': 'personal'},
                   DIRECT: {'label': 'displayForm'},
                   RULES: {'source': {RULE: '"VIAF"'},
                           'uri': {RULE: '"http://www.viaf.org/viaf/{p1}"',
                                   FIELDS: {'p1': 'viafid'}}}}

VIAF_PLACE_MAP = {RESULT: 'result',
                  FILTER: {'nametype': 'geographic'},
                  # only resources having the nametype "geographic" will be returned
                  DIRECT: {'label': 'displayForm'},
                  RULES: {'uri': {RULE: '"http://www.viaf.org/viaf/{p1}"',
                                  FIELDS: {'p1': 'viafid'}}}}

DBPEDIA_MAP = {RESULT: 'results',
              DIRECT: {'label': 'label',
                        'uri': 'uri'}}

GEMET_MAP = {DIRECT: {'label': 'preferredLabel',
                        'uri': 'uri'}}

FISH_MAP = {DIRECT: {'label': 'label',
                        'uri': 'uri'}}
           

# SOURCES
'''
{'URL': end point url
 'PAYLOAD': {} request payload}
'''

GND_PERSON_SOURCE = {URL: 'https://lobid.org/gnd/search',
                     QUERY_FIELD: 'q',
                     PAYLOAD: {'format':'json:suggest',
                               'filter': 'type:Person',
                               'q': None}}
    
VIAF_SOURCE =  {URL: 'http://www.viaf.org/viaf/AutoSuggest',
                QUERY_FIELD: 'query',
                PAYLOAD: {'query': None}}          

DBPEDIA_SOURCE = {URL: 'http://lookup.dbpedia.org/api/search/PrefixSearch?',
                  QUERY_FIELD: 'QueryString',
                  PAYLOAD: {'QueryString': None}}

GEMET_SOURCE = {URL: 'https://www.eionet.europa.eu/gemet/getConceptsMatchingKeyword?',
                QUERY_FIELD: 'keyword',
                PAYLOAD: {'keyword': None,
                          'search_mode': '4'}}

FISH_EVENT_TYPES_SOURCE = {URL: 'https://www.heritagedata.org/live/services/getConceptLabelMatch?',
                          QUERY_FIELD: 'contains',
                          PAYLOAD: {'contains': None,
                                    'schemeURI': 'http://purl.org/heritagedata/schemes/agl_et'}}

FISH_ARCH_SCIENCES_SOURCE = {URL: 'https://www.heritagedata.org/live/services/getConceptLabelMatch?',
                            QUERY_FIELD: 'contains',
                            PAYLOAD: {'contains': None,
                                      'schemeURI': 'http://purl.org/heritagedata/schemes/560'}}

FISH_MONUMENT_TYPES_SOURCE = {URL: 'https://www.heritagedata.org/live/services/getConceptLabelMatch?',
                              QUERY_FIELD: 'contains',
                              PAYLOAD: {'contains': None,
                                        'schemeURI': 'http://purl.org/heritagedata/schemes/eh_tmt2'}}

FISH_ARCH_OBJECTS_SOURCE = {URL: 'https://www.heritagedata.org/live/services/getConceptLabelMatch?',
                            QUERY_FIELD: 'contains',
                            PAYLOAD: {'contains': None,
                                      'schemeURI': 'http://purl.org/heritagedata/schemes/mda_obj'}}

