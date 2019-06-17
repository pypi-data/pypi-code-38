"""

  ____       _ ____  _ _         _____ _____ ____  __  __ _ _         _____           _ _    _ _
 / ___|  ___(_) __ )(_) |_ ___  |_   _| ____|  _ \|  \/  (_) |_ ___  |_   _|__   ___ | | | _(_) |_
 \___ \ / __| |  _ \| | __/ _ \   | | |  _| | |_) | |\/| | | __/ _ \   | |/ _ \ / _ \| | |/ / | __|
  ___) | (__| | |_) | | ||  __/   | | | |___|  _ <| |  | | | ||  __/   | | (_) | (_) | |   <| | |_
 |____/ \___|_|____/|_|\__\___|   |_| |_____|_| \_\_|  |_|_|\__\___|   |_|\___/ \___/|_|_|\_\_|\__|


TExpressRequestBuilder- make requests to the TExpress API and process results.

"""

__author__ = 'SciBite DataScience'
__version__ = '0.2'
__copyright__ = '(c) 2019, SciBite Ltd'
__license__ = 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License'

import requests
import os
import pandas as pd


class TexpressRequestBuilder():
    """
    Class for creating TEXPress requests.
    """

    def __init__(self):
        self.url = 'http://localhost:9090/termite'
        self.input_file_path = ''
        self.payload = {"output": "json", "method": "texpress"}
        self.options = {}
        self.binary_content = None
        self.basic_auth = ()
        self.verify_request = True

    def set_basic_auth(self, username='', password='', verification=True):
        """
        Pass basic authentication credentials.
        **ONLY change verification if you are calling a known source**

        :param username: username to be used for basic authentication
        :param password: password to be used for basic authentication
        :param verification: if set to False requests will ifnore verifying the SSL certificate, can also pass the path to a certfile
        :return:
        """
        self.basic_auth = (username, password)
        self.verify_request = verification

    def set_url(self, url):
        """
        Set the URL of the TERMite instance e.g. for local instance http://localhost:9090/termite

        :param url: the URL of the TERMite instance to be hit
        :return:
        """
        self.url = url

    def set_binary_content(self, input_file_path):
        """
        For annotating file content, send file path string and process file as a binary
        multiple files of the same type can be scanned at once if placed in a zip archive.
        
        :param input_file_path: file path to the file to be sent to TERMite
        :return: 
        """
        file_obj = open(input_file_path, 'rb')
        file_name = os.path.basename(input_file_path)
        self.binary_content = {"binary": (file_name, file_obj)}

    def set_text(self, string):
        """
        Use this for tagging raw text e.g. if looping through some file content
    
        :param string: text to be sent to TERMite
        :return: 
        """
        self.payload["text"] = string

    def set_options(self, options_dict):
        """
        For bulk setting multiple TERMite API options in a single call, send a dictionary object here
        
        :param options_dict: a dictionary of options to be passed to TERMite
        :return: 
        """
        to_payload = ['output', 'bundle', 'pattern', 'method']
        options = []

        for key, value in options_dict.items():
            if key in to_payload:
                self.payload[key] = value
            else:
                options.append(key + "=" + str(value))

        option_string = '&'.join(options)
        if "opts" in self.payload:
            self.payload["opts"] = option_string + "&" + self.payload["opts"]
        else:
            self.payload["opts"] = option_string

    #######
    # individual options for applying the major TERMite settings
    #######

    def set_fuzzy(self, bool):
        """
        Use fuzzy matching?
        
        :param bool: set to True if fuzzy matching is to be enabled
        :return: 
        """
        input = bool_to_string(bool)
        if "opts" in self.payload:
            self.payload["opts"] = "fzy.promote=" + input + "&" + self.payload["opts"]
        else:
            self.payload["opts"] = "fzy.promote=" + input
        self.payload["fuzzy"] = input

    def set_subsume(self, bool):
        """
        If another TExpress hit full overlaps this hit, hits to this pattern are removed
        
        :param bool: set subsume if True
        :return: 
        """
        input = bool_to_string(bool)
        self.payload["tx.subsumable"] = input

    def set_entities(self, string):
        """
        Limit the entities to be annotated
        
        :param string: a comma separated string of entity types, e.g. 'DRUG,GENE'
        :return: 
        """
        self.payload["entities"] = string

    def set_input_format(self, string):
        """
        Set input format e.g. txt, medline.xml, node.xml, pdf, xlsx
        
        :param string: 
        :return: 
        """
        self.payload["format"] = string

    def set_output_format(self, string):
        """
        Set output format e.g. tsv, json, doc.json
        
        :param string: 
        :return: 
        """
        self.payload["output"] = string

    def set_max_docs(self, integer):
        """
        When tagging a zip file of multiple documents, limit how many to scan
        also applies where there are multiple document records in a single xml e.g. from a medline XML export
        
        :param integer: number of documents to limit annotation too
        :return: 
        """
        self.payload["maxDocs"] = integer

    def set_no_empty(self, bool):
        """
        Reject all documents where there were no hits
        
        :param bool: if True do not return any docs with no hits
        :return: 
        """
        input = bool_to_string(bool)
        self.payload["noEmpty"] = input

    def execute(self, display_request=False):
        """
        Once all settings are done, POST the parameters to the TERMite RESTful API

        :param display_request: if True request will be printed out before being submitted
        :return:
        """
        if display_request:
            print("REQUEST: ", self.url, self.payload)
        try:
            if self.binary_content and bool(self.basic_auth):
                response = requests.post(self.url, data=self.payload, files=self.binary_content, auth=self.basic_auth,
                                         verify=self.verify_request)
            elif self.binary_content and bool(self.basic_auth) == False:
                response = requests.post(self.url, data=self.payload, files=self.binary_content)
            elif not self.binary_content and bool(self.basic_auth):
                response = requests.post(self.url, data=self.payload, verify=self.verify_request, auth=self.basic_auth)
            else:
                response = requests.post(self.url, data=self.payload)
        except Exception as e:
            return print(
                "Failed with the following error {}\n\nPlease check that TERMite can be accessed via the following URL {}\nAnd that the necessary credentials have been provided (done so using the set_basic_auth() function)".format(
                    e, self.url))

        if self.payload["output"] in ["json", "doc.json", "doc.jsonx"]:
            return response.json()
        else:
            return response.text

    ######
    # Bespoke methods for TExpress
    #   |
    #   V
    ######

    def set_allow_ambiguous(self, bool):
        """
        Allow matches containing ambiguous entity hits to be returned.

        :param bool:
        :return:
        """
        input = bool_to_string(bool)
        if "opts" in self.payload:
            self.payload["opts"] = self.payload["opts"] + "&tx.ambig=" + input
        else:
            self.payload["opts"] = "tx.ambig=" + input

    def set_alwaysadd(self, bool):
        """
        Set input format e.g. txt, medline.xml, node.xml, pdf, xlsx

        :param string:
        :return:
        """
        self.payload["alwaysAdd"] = bool_to_string(bool)

    def set_pivot(self, bool):
        """
        Set input format e.g. txt, medline.xml, node.xml, pdf, xlsx

        :param string:
        :return:
        """
        self.payload["pivot"] = bool_to_string(bool)

    def set_tx_group(self, bool):
        """
        Set input format e.g. txt, medline.xml, node.xml, pdf, xlsx

        :param string:
        :return:
        """
        self.payload["tx.groups"] = bool_to_string(bool)

    def set_bundle(self, bundle_name):
        """
        Provide a bundle to be used during TExpress search.
        Please ensure that this bunndle is loaded on the server which you are calling.

        :param bundle_name:
        :return:
        """

        self.payload["bundle"] = bundle_name

    def set_pattern(self, bundle_name):
        """
        Provide a pattern to be used during TExpress search.

        :param bundle_name:
        :return:
        """

        self.payload["pattern"] = bundle_name

    def set_reverse(self, bool):
        """
        Should we look for this reverse version of this pattern?

        :param bundle_name:
        :return:
        """

        input = bool_to_string(bool)
        if "opts" in self.payload:
            self.payload["opts"] = "reverse=" + input + "&" + self.payload["opts"]
        else:
            self.payload["opts"] = "reverse=" + input
        self.payload["reverse"] = input

    ######
    #   ^
    #   |
    # Bespoke methods for TExpress
    ######


def bool_to_string(bool):
    """
    Convert a boolean to a string
    
    :param bool: provide boolean to be converted
    :return: 
    """
    string = str(bool)
    string = string.lower()

    return string


def annotate_files(url, input_file_path, options_dict):
    """
    Wrapper function to execute a TExpress request for annotating individual files or a zip archive
    
    :param url: url of TERMite instance
    :param input_file_path: path to file to be annotated
    :param options_dict: dictionary of options to be used during annotation
    :return: 
    """
    t = TexpressRequestBuilder()
    t.set_url(url)
    t.set_binary_content(input_file_path)
    t.set_options(options_dict)
    result = t.execute()

    return result


def annotate_text(url, text, options_dict):
    """
    Wrapper function to execute a TExpress request for annotating strings of text
    
    :param url: url of TERMite instance
    :param input_file_path: path to file to be annotated
    :param options_dict: dictionary of options to be used during annotation
    :return: 
    """
    t = TexpressRequestBuilder()
    t.set_url(url)
    t.set_text(text)
    t.set_options(options_dict)
    result = t.execute()

    return result


def process_payload(texpress_hits, response_payload, doc_id='', score_cutoff=0,
                    remove_subsumed=True):
    """
    Parses the termite json output to filter out only entity types of interest and their major metadata
    includes rules for rejecting ambiguous or low-relevance hits
    
    :param texpress_hits: texpress hits to be processed
    :param response_payload: total payload
    :param doc_id: document id
    :param score_cutoff: a numeric value between 1-5
    :param remove_subsumed: boolean
    :return: 
    """

    for pattern_id in response_payload:
        for matches in response_payload[pattern_id]:
            entity_names = matches["entityNames"]
            for match in matches['matches']:
                pattern_id = match["pattern_id"]
                conf_score = match["conf"]
                subsumed = match["subsumed"]
                original_frag = match["originalFragment"]
                match_entities = match["matchEntities"]
                all_entity_info = []
                for x in match_entities:
                    all_entity_info.append('{}#{}'.format(x, entity_names.get(x)))
                if remove_subsumed and subsumed == 'true':
                    continue
                if conf_score < score_cutoff:
                    continue
                elif pattern_id in texpress_hits:
                    texpress_hits[pattern_id].append(
                        {'doc_id': doc_id, 'entities': all_entity_info, 'original_fragment': original_frag,
                         'conf': conf_score})
                else:
                    texpress_hits[pattern_id] = [
                        {'doc_id': doc_id, 'entities': all_entity_info, 'original_fragment': original_frag,
                         'conf': conf_score}]

    return texpress_hits


def get_entity_hits_from_json(termite_json_response, score_cutoff=0):
    """
    Remove the entity hits from returned TExpress JSON and return a dictionary in the format
    (pattern_id : (orig_sentence, [entities]))
    
    :param termite_json_response: JSON returned from TExpress
    :param score_cutoff: a numeric value between 1-5
    :return: 
    """

    filtered_hits = {}

    if "RESP_TEXPRESS" in termite_json_response:
        doc_results = termite_json_response["RESP_TEXPRESS"]
        for doc_id, response_payload in doc_results.items():
            filtered_hits = process_payload(filtered_hits, response_payload, score_cutoff=score_cutoff, doc_id=doc_id)

    return filtered_hits


######
#
# Methods for manipulating returned JSON into pandas dataframe
#   |
#   v
######

def json_resp_records(json_resp_texpress, remove_subsumed=True):
    """
    parses JSON RESP_TEXPRESS into records, includes filter to remove subsumed hits.

    :param json_resp_texpress: RESP_TEXPRESS of TExpress JSON response
    :param removeSubsumed: boolean
    :return: TExpress hits in records format
    """

    hits = []
    for docID, patterns in json_resp_texpress.items():
        for pattern_id, pattern_matches in patterns.items():
            if len(pattern_matches) is not 0:
                for pattern_hits in pattern_matches:
                    for match in pattern_hits['matches']:
                        match['docID'] = docID
                        match['patternID'] = pattern_id
                        for x in pattern_hits:
                            if x == "matches":
                                continue
                            elif x == "meta":
                                for k, v in pattern_hits[x].items():
                                    match[k] = v
                            else:
                                match[x] = pattern_hits[x]
                        if remove_subsumed is True and match['subsumed'] is True:
                            continue
                        else:
                            hits.append(match)

    return (hits)


def docjsonx_records(docjsonx_response, remove_subsumed=True):
    """
    Parses doc.JSONx TExpress into records, includes filter to remove subsumed hits.

    :param docjsonx_response: TExpress doc.JSONx response
    :param remove_subsumed: boolean
    :return: TExpress hits in records format
    """

    hits = []
    for doc in docjsonx_response:
        for patternID, pattern_matches in doc['texpressTags'].items():
            if len(pattern_matches) is not 0:
                for pattern_hits in pattern_matches:
                    for match in pattern_hits['matches']:
                        match['patternID'] = patternID
                        match.update(pattern_hits)
                        match.update(doc)
                        del (match['matches'])
                        del (match['texpressTags'])
                        if remove_subsumed is True and match['subsumed'] is True:
                            continue
                        else:
                            hits.append(match)

    return (hits)


def texpress_records(texpress_response, remove_subsumed=True):
    """
    Parses TExpress JSON or doc.JSONx response into records, with filtering to remove subsumed hits.

    :param texpress_response: TExpress JSON of doc.JSONx response
    :param remove_subsumed: boolean
    :return: records of TExpress hits
    """

    if 'RESP_TEXPRESS' in texpress_response:
        records = json_resp_records(texpress_response['RESP_TEXPRESS'], remove_subsumed=remove_subsumed)
    else:
        records = docjsonx_records(texpress_response, remove_subsumed=remove_subsumed)

    return (records)


def get_texpress_dataframe(texpress_response, cols_to_add="", remove_subsumed=True):
    """

    :param texpress_response:
    :param cols_to_add:
    :param remove_subsumed:
    :return:
    """

    texpressRecords = texpress_records(texpress_response, remove_subsumed=remove_subsumed)
    df = pd.DataFrame(texpressRecords)

    cols = ["docID", "patternID", "originalFragment", "matchEntities", "originalSentence",
            "sentence", "subsumed"]

    if cols_to_add:
        cols_to_add = cols_to_add.replace(" ", "").split(",")
        try:
            cols = cols + cols_to_add
            return (df[cols])
        except KeyError as e:
            print("Invalid column selection.", e)
    else:
        return (df[cols])
