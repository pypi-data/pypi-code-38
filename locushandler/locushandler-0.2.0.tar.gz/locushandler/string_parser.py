"""
String parser for Locus strings. Parse a Locus string
to dict or list or string at specified levels of granularity
"""
import locushandler.params as par
import locushandler.string_helpers as shlp
import locushandler.validation as val


def string_parser(locus_field, output_type, granularity="full",
                  show_dr=False, show_io=False, merge_fields=False, validate=True):
    '''
    Read through the input string and identify the different Loci within
    the string.
    Calls work_parser and resource_parser on work and resource loci.
    The output type is specified by the user.

    Dependencies :
    call : work_parser, resource_parser

    :param locus_field: (string) locus code to parse
    :param output_type: (string) 'list', 'str' or 'dict'
    :param granularity: (string) granularity 'actxres'
    :param dr: (bool) True if need dr else False (optional, default=False)
    :param io: (bool) True if need io else False (optional, default=False)
    :param merge_fields: (bool) True if need resource and activity subfields concatenated 
                         in return dict (optional, default=False)
    :param validate: (string) True to activate validation of Locus codes (optional, default=True)
    :return : (string, dict or list)
    '''
    field_type = shlp.work_or_resource(locus_field)
    if field_type == 'work':
        return work_parser(locus_field, output_type, granularity,
                           show_dr=show_dr, show_io=show_io, merge_fields=merge_fields, 
                           validate=validate)
    else:
        return resource_parser(locus_field, output_type, granularity,
                               validate=validate, merge_fields=merge_fields)

def work_parser(locus_field, output_type, granularity, show_dr=True, show_io=True, merge_fields=False, validate=True):
    '''
    Read through the input string and identify each element at the finest
    granularity level.
    Return all those elements or only the one of interest based on the
    granularity argument.

    Dependencies :
    is called : string_parser

    :param locus_field: (string) locus code to parse
    :param output_type: (string) 'list', 'str' or 'dict'
    :param granularity: (string) granularity 'actxres'
    :param show_dr: (bool) True if need dr else False (optional, default=True)
    :param show_io: (bool) True if need io else False (optional, default=True)
    :param merge_fields: (bool) True if need resource and activity subfields concatenated 
                         in return dict (optional, default=False)
    :param validate: (string) True to activate validation of Locus codes (optional, default=True)
    :return : (string, dict or list)
    '''
    assert isinstance(output_type, str), 'Expect output_type to be a string'
    assert output_type in par.LOCUS_OUTPUT_TYPE, f'Expect output_type to be from {par.LOCUS_OUTPUT_TYPE}'

    dr, io = shlp.extract_dr_io(locus_field)
    dr = dr if show_dr else None
    io = io if show_io else None

    locus_verb, locus_object = shlp.remove_dr_io(locus_field).split()
    verb_granularity, noun_granularity = shlp.parse_granularity(granularity)

    parsed_dict = work_dict_parser(dr, locus_verb, locus_object, io,
                                verb_granularity, noun_granularity)
 
    # call validation before further formatting
    if validate:
        try:
            val.validate_locus(parsed_dict)
        except val.LocusValidationError as e:
            raise(e)

    if output_type == 'dict':
        if merge_fields:
            return concat_work_fields(parsed_dict)     
        return parsed_dict
    elif output_type == 'list':
        return work_list_parser(parsed_dict)
    elif output_type == 'string':
        return work_string_parser(parsed_dict)
    
def work_string_parser(parsed_dict):
    '''
    Convert parsed dictionary to string

    Dependencies : 
    call : concat_work_fields

    :param parsed_dict: (dict)
    :return : (string)
    '''
    fields = concat_work_fields(parsed_dict)
    dr = fields['dr']
    act = fields['act']
    obj = fields['obj']
    io = fields['io']
    return f'{dr} {act} {obj} {io}'.strip()

def concat_work_fields(parsed_dict):
    '''
    Manipulate dictionary to not separate subfields of a 
    resource or activity
    :param parsed_dict: (dict) 
    :return : (dict) dictionary with (field, field_value) pairs
    '''
    act = parse_verb_to_string(parsed_dict['act'])
    obj = parse_noun_to_string(parsed_dict['obj'])

    # dr, io not always there. Have them be empty substrings
    # for concatenation later if that's the case
    show_dr = parsed_dict.get('dr')
    show_io = parsed_dict.get('io')
    if show_dr:
        dr = parse_noun_to_string(parsed_dict['dr'])
    else:
        dr = ''
    if show_io:
        io = parse_noun_to_string(parsed_dict['io'])
    else:
        io = ''
    return {'dr':dr, 'act':act, 'obj':obj, 'io':io}


def work_list_parser(parsed_dict):
    '''
    Convert parsed dictionary list
    :param parsed_dict: (dict)
    :return : (list)
    '''
    return _unravel_nested_dict_to_list(parsed_dict)

def work_dict_parser(dr, locus_verb, locus_object, io,
                     verb_granularity, noun_granularity):
    '''
    Read through input strings and parse to dict
    :param dr: (string)
    :param locus_verb: (string)
    :param locus_object: (string)
    :param io: (string)
    :param verb_granularity: (string)
    :param noun_granularity: (string)
    :return : (dict)
    '''
    assert isinstance(
        verb_granularity, str), 'Expect verb_granularity to be a string'
    assert isinstance(
        noun_granularity, str), 'Expect noun_granularity to be a string'

    parsed = {}
    if dr != None:
        parsed['dr'] = {}
    parsed['act'] = {}
    parsed['obj'] = {}
    if io != None:
        parsed['io'] = {}
    # if we choose to exclude dr, io
    # their values would be None --> do not initialize field
    # if we choose to include but dr, io not found
    # their values would be empty string

    noun_fields = par.RES_GRAN_TO_FIELDS[noun_granularity]
    for field in noun_fields:
        parsed['obj'][field] = noun_parser(
            locus_object)[field]

        if dr != None:
            parsed['dr'][field] = noun_parser(dr)[field]
        if io != None:
            parsed['io'][field] = noun_parser(io)[field]

    verb_fields = par.ACT_GRAN_TO_FIELDS[verb_granularity]
    for field in verb_fields:
        parsed['act'][field] = verb_parser(locus_verb)[field]

    return parsed


def resource_parser(locus_field, output_type, granularity, merge_fields=False, validate=True):
    '''
    Read through the input string and identify each element at the finest
    granularity level.
    Return all those elements or only the one of interest based on the
    granularity argument.

    Dependencies:
    is called: string_parser

    :param locus_field: (string)
    :param output_type: (string) from par.LOCUS_OUTPUT_TYPE
    :param granularity: (string) from GRANULARITY
    :param merge_fields: (bool) True if need resource and activity subfields concatenated 
                         in return dict (optional, default=False)
    :param validate: (string) True to activate validation of Locus codes (optional, default=True)
    :return: parsed : (string, dict or list)
    '''
    assert isinstance(output_type, str), 'Expect output_type to be a string'
    assert output_type in par.LOCUS_OUTPUT_TYPE, f'Expect output_type to be from {par.LOCUS_OUTPUT_TYPE}'

    locus_subject, locus_verb, locus_object = locus_field.split()
    verb_granularity, noun_granularity = shlp.parse_granularity(granularity)
    
    parsed_dict = resource_dict_parser(locus_subject, locus_verb, locus_object,
                                    verb_granularity, noun_granularity)
 
    # call validation on locus before further formatting
    if validate:    
        try:
            val.validate_locus(parsed_dict)
        except val.LocusValidationError as e:
            raise(e)
    
    if output_type == 'dict':
        if merge_fields:
            return concat_resource_fields(parsed_dict)
        return parsed_dict
    elif output_type == 'list':
        return resource_list_parser(parsed_dict)
    elif output_type == 'string':
        return resource_string_parser(parsed_dict)


def resource_string_parser(parsed_dict):
    '''
    Convert parsed resource dictionary to string

    Dependencies : 
    call : concat_resource_fields

    :param parsed_dict: (dict)
    :return : (string)
    '''
    fields = concat_resource_fields(parsed_dict)
    subj = fields['subj']
    act = fields['act']
    obj = fields['obj']
    return f'{subj} {act} {obj}'

def concat_resource_fields(parsed_dict):
    '''
    Manipulate dictionary to not separate subfields of a 
    resource or activity
    :param parsed_dict: (dict) 
    :return : (dict) dictionary with (field, field_value) pairs
    '''
    subj = parse_noun_to_string(parsed_dict['subj'])
    act = parse_verb_to_string(parsed_dict['act'])
    obj = parse_noun_to_string(parsed_dict['obj'])

    return {'subj':subj, 'act':act, 'obj':obj}


def resource_list_parser(parsed_dict):
    '''
    Convert parsed dictionary to a list
    :param parsed_dict: (dict)
    :return: (list)
    '''
    return _unravel_nested_dict_to_list(parsed_dict)

def resource_dict_parser(locus_subject, locus_verb, locus_object,
                         verb_granularity, noun_granularity):
    '''
    Read through input strings and parse to dict
    :param locus_subject: (string)
    :param locus_verb: (string)
    :param locus_object: (string)
    :param verb_granularity: (string)
    :param noun_granularity: (string)
    :return : (dict)
    '''
    assert isinstance(
        verb_granularity, str), 'Expect verb_granularity to be a string'
    assert isinstance(
        noun_granularity, str), 'Expect noun_granularity to be a string'

    parsed = {'subj': {}, 'act': {}, 'obj': {}}

    noun_fields = par.RES_GRAN_TO_FIELDS[noun_granularity]
    for field in noun_fields:
        parsed['subj'][field] = noun_parser(
            locus_subject)[field]
        parsed['obj'][field] = noun_parser(
            locus_object)[field]

    verb_fields = par.ACT_GRAN_TO_FIELDS[verb_granularity]
    for field in verb_fields:
        parsed['act'][field] = verb_parser(locus_verb)[field]

    return parsed


def verb_parser(locus_verb):
    '''
    Given single Locus verb (e.g. 1.3.2), parse
    to full granularity.
    :param locus_verb: (string)
    :return : (dict)
    '''
    assert isinstance(
        locus_verb, str), f'Expect locus_verb: {locus_verb} to be a string'
    if locus_verb.lower() in par.DIVS:
        act_4, act_12, act_36 = 'V', 'V', 'V'
    else:
        act_4, act_12, act_36 = locus_verb.split('.')

    return {'act_4': act_4, 'act_12': act_12, 'act_36': act_36}


def noun_parser(locus_noun):
    '''
    Given single Locus noun (e.g. C4iii), parse
    to full granularity.
    :param locus_noun: (string)
    :return : (dict)
    '''
    assert isinstance(
        locus_noun, str), f'Expect locus_noun: {locus_noun} to be a string'

    if locus_noun == 'F':
        category, stage, substage = 'F', 'V', 'V'
    elif locus_noun == '':
        category, stage, substage = '', '', ''
    else:
        category, stage, substage = shlp.dediv_noun(locus_noun)

    return {'category': category, 'stage': stage, 'substage': substage}

# HELPER for functions that parse to strings


def parse_noun_to_string(locus_noun_field):
    '''Given parse dictionary field that is a locus noun
    Parse to appropriate string, handling Div's and F
    :param locus_noun_field: (dict)
    :return : (string)
    '''
    to_parse = []
    for value in locus_noun_field.values():
        if value == 'V':
            to_parse.append(value)
            return ''.join(to_parse)
        elif value == 'F':
            # F has no staging
            return 'F'
        else:
            to_parse.append(value)
    return ''.join(to_parse)


def parse_verb_to_string(locus_verb_field):
    '''Given parse dictionary field that is a locus verb
    Parse to appropriate string, handling Div's
    :param locus_noun_field: (dict)
    :return : (string)
    '''
    to_parse = []
    for value in locus_verb_field.values():
        if value == 'V':
            # the whole resource is Div, return immediately
            return 'V'
        else:
            to_parse.append(value)
    return '.'.join(to_parse)


# HELPERS that are not specific to Locus
def _unravel_nested_dict_to_list(nested_dict):
    '''
    Flatten doubly nested dict to a list.
    :param: nested_dict - a 2-level nested dict
    :return : (list) - a 1-D list of values
    parsed from nested_dict
    '''
    parsed_list = []
    for field in nested_dict.values():
        for val in field.values():
            parsed_list.append(val)
    return parsed_list
