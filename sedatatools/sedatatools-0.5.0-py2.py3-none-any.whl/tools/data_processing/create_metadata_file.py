"""
This script will generate metadata file
v2.4
"""

from lxml import etree as et
from lxml.builder import ElementMaker
import uuid
import pymssql
import csv
import os
import yaml
import sys
import collections  # used for dictionary sorting
import datetime  # used for validation
import optparse
from sys import argv


def get_table_fipses(table_fips, geo_level_info):
    """
    This will create a string with list of FIPS columns (SL050_FIPS, SL040_FIPS, etc.) based on nesting information
    (DB Conn. Info) to be used as primary keys.
    :param table_fips: Fips code for the geo that table is on e.g. for county level table it's FIPS_SL050
    :param geo_level_info: GeoInfo from config file
    :return: String with list of FIPS columns
    """
    # this list should always return just one element, if not then sumlevs are not unique
    low_fips_pos = [i for i, k in enumerate(geo_level_info) if k[0] == table_fips.replace('_FIPS', '')][0]
    full_fips_list = [table_fips]
    for i in reversed(range(low_fips_pos)):
        # stop adding sumlevs if you find geo level with indent 0 or fips length of 0
        if geo_level_info[i][4] == 0 or geo_level_info[i][2] == '0':
            break
        # if you find sumlev with same indent as previous or greater than wanted then skip it
        if geo_level_info[i][4] == geo_level_info[i + 1][4] or geo_level_info[i][4] >= geo_level_info[low_fips_pos][4]:
            continue

        full_fips_list.append(geo_level_info[i][0] + '_FIPS')

    full_fips_list = ','.join(list(reversed(full_fips_list)))
    return full_fips_list


def get_config(config_file):
    with open(config_file, 'r') as conf:
        config = yaml.load(conf)
    return config


def create_acronym(full_string):
    """
    Create acronym from a multi word full_string, in case only one word is in full_string it will capitalize it.
    :param full_string: String to create acronym from
    :return:
    """
    chars_for_removal = ['(', ')', '&', '/', ',', '.', '\\', '\'', '&', '%', '#']
    for ch in chars_for_removal:
        if ch in full_string:
            full_string = full_string.replace(ch, ' ')
    full_string = full_string.strip()
    while '  ' in full_string:
        full_string = full_string.replace('  ', ' ')
    if ' ' in full_string:
        blank_pos = [i for i, letter in enumerate(full_string) if letter == ' ']
        acronym = full_string[0] + ''.join([full_string[i + 1] for i in blank_pos]).upper()
    else:
        acronym = full_string.upper()
    return acronym


def get_table_metadata_from_db(server, dbname, user, password, project_year, trusted_connection):
    """
    Get table descriptions from table_names table in database, make it prettier and return it as a dictionary
    :param server: Server address
    :param dbname: Database names
    :param user: username for sql server
    :param password: password for sql server
    :param project_year: project year for which the data is relevant
    :param trusted_connection: flag if server credentials are needed
    :return: Dictionary of metadata tables
    """
    # extensions to remove from input file e.g. Sex_by_Age.csv > Sex_by_Age
    extension = ['.txt', '.csv', '.tsv']
    meta_table_dictionary = {}

    if trusted_connection:
        conn = pymssql.connect(host=server, database=dbname)
    else:
        conn = pymssql.connect(host=server, database=dbname, user=user, password=password)

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM table_names where projectYear = ' + project_year)
    table_names = cursor.fetchall()

    # exit if table_names table empty
    if len(table_names) == 0:
        print("Error: Table names does not exist in database!")
        sys.exit()

    meta_data = []
    for ext in extension:
        for el in table_names:
            if ext in el[0]:
                # remove extension and data set ID (everything until first '_')
                meta_data.append([el[0].replace(ext, '')[el[0].index('_') + 1:], el[1]])

    for i in meta_data:
        meta_table_dictionary[i[1]] = i[0].replace('_', ' ')

    return meta_table_dictionary


def check_data_type(datum):
    """
    This function checks type of value because pymssql cannot distinguish int from float
    :param datum: Value to be checked
    :return:
    """
    if datum == 'int':
        return 3
    elif datum == 'float':
        return 2
    elif 'char' in datum:
        return 1
    elif datum is None:
        return 9
    else:
        print("Undefined data type in source data for: ", datum)  # if nothing then string


def get_tables_from_db(server, dbname, project_year, user, password, trustedConnection):
    """
    Get list of tables from db, make it unique on metadata level and return it as a dictionary
    :param server: server name
    :param dbname: database name
    :param project_year:  project year for which the data is relevant
    :param user: username for sql server
    :param password: username for sql server
    :param trustedConnection: flag if server credentials are needed
    :return: list of tables in database
    """

    if trustedConnection:
        conn = pymssql.connect(server=server, database=dbname)  # for trusted connection
    else:
        conn = pymssql.connect(host=server, database=dbname, user=user, password=password)

    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sys.objects WHERE type_desc = 'USER_TABLE' AND name <> 'table_names' and left("
                   "name,1) <> '_' and name like '%" + str(project_year) + "%' AND name <> 'sysdiagrams' ORDER BY "
                                                                           "modify_date")

    table_list = [str(*i) for i in cursor.fetchall() if i != 'table_names']
    dict_tables_and_vars = {}
    cursor = conn.cursor()
    for i in table_list:
        sqlTab = 'SELECT * FROM ' + i

        sql = "select DATA_TYPE from information_schema.columns where TABLE_NAME = '" + i + "'"
        cursor.execute(sql)
        list_of_types = cursor.fetchall()
        var_types = [check_data_type(datum[0]) for datum in list_of_types]
        cursor.execute(sqlTab)
        dict_tables_and_vars[i] = [j[0] for j in cursor.description]
        attrib_type = [j[1] for j in cursor.description]
        dict_tables_and_vars[i] = list(zip(dict_tables_and_vars[i], var_types, attrib_type))
    conn.close()

    dict_tables_and_vars_unique = {}
    for key, value in dict_tables_and_vars.items():
        values = []
        pos_t = [i for i, k in enumerate(key) if k == '_'][1] + 1
        for v in value:
            # skip system required names
            if len([j for j, l in enumerate(v[0]) if l == '_']) < 3:
                continue
            pos_v = [j for j, l in enumerate(v[0]) if l == '_'][2] + 1
            # print(key[pos_t:])
            # print(v[0][pos_v:])
            values.append([v[0][pos_v:], v[1]])
        dict_tables_and_vars_unique[key[pos_t:]] = values

    return dict_tables_and_vars


def get_variable_descriptions_from_file(variable_description_location):
    """
    Open file and read variable names and its description. Files must be in format: variable_id, description
    :param variable_description_location: Full path to the file
    :return: Dictionary with variable id as key and its description as a value
    """
    file_content_dict = {}
    with open(variable_description_location) as file:
        reader = csv.reader(file)
        for var in list(reader):
            if len(var) == 0:
                print("Info: Skipping empty line while reading variable description file.")
                continue
            if len(var) == 2:
                file_content_dict[var[0]] = [var[1]]  # remove any commas if they exist
            else:
                file_content_dict[var[0]] = [var[1], var[2]]  # remove any commas if they exist
    return file_content_dict


def get_variable_descriptions_from_directory(variable_description_location):
    """
    In case folder is provided, take a list of its files and read it vor variable description
    :param variable_description_location: Full path to the folder with files
    :return: Dictionary with variable id as key and its description as a value
    """
    os.chdir(variable_description_location)
    file_list = os.listdir()
    file_content_dict = {}
    for fileName in file_list:
        file_content_dict.update(get_variable_descriptions_from_file(fileName))
    return file_content_dict


def get_geotype(geo_level_info):  # number of geo types
    """
    Get list of geotypes in project
    :param geo_level_info: List from config file
    :return:
    """
    e = ElementMaker()
    sum_levs = geo_level_info  # getGeoNesting(geoLevelInfoFilePath)
    plural_forms = {'County': 'Counties', 'State': 'States'}
    for i in sum_levs:
        if i[1] not in sum_levs:
            plural_forms[i[1]] = i[1]

    # create names of relevant geos
    relevant_geos = ','.join([create_acronym(i[1]) for i in sum_levs])

    result = []

    for sumlev in sum_levs:
        partial_fips_field = create_acronym(sumlev[1])
        result.append(e.geoType(e.Visible('true'),
                                GUID=str(uuid.uuid4()),
                                Name=sumlev[0],
                                Label=sumlev[1],
                                QLabel=sumlev[1],
                                RelevantGeoIDs='FIPS,NAME,QName,' + relevant_geos,
                                PluralName=plural_forms[sumlev[1]],
                                fullCoverage='true',
                                majorGeo='true',
                                # GeoAbrev = sumlev[0],#'us, nation', COMMENTED BECAUSE IN ACS 2011 EXAMPLE IT WAS
                                # MISSING!?
                                Indent=str(int(sumlev[4])),
                                Sumlev=sumlev[0].replace('SL', ''),
                                FipsCodeLength=sumlev[2],
                                FipsCodeFieldName='FIPS',
                                FipsCodePartialFieldName=partial_fips_field,
                                FipsCodePartialLength=str(sumlev[3]))
                      )
    return result


def get_datasets(connection_string, dbname, geo_level_info, project_id, user, password, server, trusted_connection):
    """
    Get data sets for the project.
    :param connection_string: Info from config file
    :param dbname: Info from config file
    :param geo_level_info: Info from config file
    :param project_id: Info from config file
    :param user: Info from config file
    :param password: Info from config file
    :param server: Info from config file
    :return: List of data sets
    """
    E = ElementMaker()
    result = []

    sum_levs = geo_level_info
    for i in sum_levs:
        geo_id_suffix = get_geo_id_db_table_name(i[0], dbname, user, password, server, project_id, trusted_connection)

        result.append(E.dataset(GUID=str(uuid.uuid4()),
                                GeoTypeName=i[0],  # SL040
                                DbConnString=connection_string,
                                DbName=dbname,
                                GeoIdDbTableName=project_id + '_' + i[0] + geo_id_suffix,
                                # tablename e.g. 'LEIP1912_SL040_PRES_001'
                                IsCached='false',
                                DbTableNamePrefix=project_id + '_' + i[0] + '_',
                                # tablename prefix e.g. 'LEIP1912_SL040_PRES_'
                                DbPrimaryKey=get_table_fipses(i[0] + '_FIPS', geo_level_info),  # this is fixed
                                DbCopyCount='1'))
    return result


def get_geo_id_db_table_name(sumlev, dbname, user, password, server, project_id, trusted_connection):
    """
    Find suffix of first table for specific geography and return it together with preceding '_'.

    :param sumlev: Summary level for which it is necessary to find suffix
    :param dbname: Database name
    :param user: Username
    :param password: Password
    :param server: Server name
    :return: Suffix off the first geography for that table
    """
    if trusted_connection:
        conn = pymssql.connect(host=server, database=dbname)
    else:
        conn = pymssql.connect(host=server, database=dbname, user=user, password=password)

    cursor = conn.cursor()
    cursor.execute(
        "SELECT TOP 1 name FROM sys.objects WHERE type_desc = 'USER_TABLE' AND name <> 'table_names' and left(name,"
        "1) <> '_' and name like '%" + sumlev + "%' and name like '" + project_id + "%' ORDER BY name")
    table_name = cursor.fetchall()
    if not table_name:  # this is fix for sumlevels that doesn't exist in database, remove this after cancen is done
        return '_001'
    table_name = table_name[0][0]
    suffix_ind = [index for index, element in enumerate(table_name) if element == '_'][-1]
    suffix = table_name[suffix_ind:]
    return suffix


def get_variables(variables, variable_description, meta_table_name):
    """
    Get variables for original tables
    :param variables: List of variables
    :param variable_description: List of variable descriptions
    :param meta_table_name: Table name for metadata file, extracted from data file name
    :return:
    """
    result = []
    e = ElementMaker()
    # remove unwanted variables
    removal_vars = ['NAME', 'SUMLEV', 'v1', 'Geo_level', 'QName', 'TYPE', 'Geo', 'FIPS', 'Geo_orig']
    variables = [i for i in variables if i[0] not in removal_vars]
    variables = [i for i in variables if '_NAME' not in i[0] and 'FIPS' not in i[0] and 'V1' != i[0]]

    for i in variables:
        # create variable Id's for metadata as meta_table_name + variable order
        global variableCounter
        variableCounter += 1
        # meta_variable_name = meta_table_name + str(100000 + variableCounter)[-5:]

        # position after project name, sumlev, and order number, needed for variable description
        if len([index for index, chr in enumerate(i[0]) if chr == '_']) == 0:
            continue
        pos = [index for index, chr in enumerate(i[0]) if chr == '_'][1] + 1

        # create variable type
        if i[1] == 3:  # integer
            var_type = '4'
            formatting_value = '9'  # 1,234
        elif i[1] == 2:
            var_type = '7'
            formatting_value = '9'  # 1,234
        elif i[1] == 1:  # char
            var_type = '2'
            formatting_value = '0'  # none
        elif i[1] == 9 and i[2] == 3:  # none
            var_type = '7'
            formatting_value = '9'  # 1,234
        elif i[1] == 9 and i[2] == 1:
            var_type = '2'
            formatting_value = '0'  # none
        else:
            var_type = '0'
            formatting_value = '0'

        # in case unexpected variable name appear in table, print warning and skip it
        # check if range exists because it searches for the variables that doesn't exists
        if i[0][pos:] not in variable_description.keys():
            print("Warning: Undefined variable found:", i[0], i[0][pos:])
            continue

        variable_desc_for_retrieve = variable_description[i[0][pos:]]

        result.append(e.variable(  # repeated for as many times as there are variables
            GUID=str(uuid.uuid4()),
            UVID='',
            BracketSourceVarGUID='',
            BracketFromVal='0',
            BracketToVal='0',
            BracketType='None',
            FirstInBracketSet='false',
            notes='',
            PrivateNotes='',
            name=i[0],  # meta_variable_name
            label=variable_desc_for_retrieve[0],  # find variable description in dictionary, by text after pr. id and
            #  order
            qLabel='',
            indent=variable_desc_for_retrieve[1] if len(variable_desc_for_retrieve) == 2 else '0',
            # TODO add indent info from variable desc. file
            dataType=var_type,
            dataTypeLength='0',  # default to zero
            formatting=formatting_value,
            customFormatStr='',  # only for SE tables
            FormulaFunctionBodyCSharp='',  # only for SE tables
            suppType='0',
            SuppField='',
            suppFlags='',
            aggMethod='1',
            DocLinksAsString='',
            AggregationStr='Add'  # 'None'
        )
        )
    return result


def get_tables(server, dbname, variable_description, user, password, project_year, trusted_connection):
    """
    Get list of original tables from db
    :param server: Server name
    :param dbname: Database name
    :param variable_description: List to decode variable names into descriptions (from variable_descriptions file)
    :param user: Username for server
    :param password: Password for server
    :param project_year: Project year
    :return: list with constructed tables tags
    """
    table_list = get_tables_from_db(server, dbname, project_year, user, password, trusted_connection)
    table_list = collections.OrderedDict(sorted(table_list.items()))
    table_meta_dictionary = get_table_metadata_from_db(server, dbname, user, password, project_year, trusted_connection)
    E = ElementMaker()
    result = []
    duplication_check_list = []

    for k, v in table_list.items():

        cut_pos = [i for i, el in enumerate(k) if el == '_']

        if (k[:cut_pos[0]] + k[cut_pos[-1] + 1:]) in duplication_check_list:  # if table is already added, skipp it
            continue

        duplication_check_list.append(
            k[:cut_pos[0]] + k[cut_pos[-1] + 1:]
        )
        # create table ID's for metadata
        global tableCounter
        tableCounter += 1
        meta_table_name = k[:cut_pos[0]] + '_' + k[cut_pos[
                                                       -1] + 1:]  # this defines how table Id will be presented in metadata
        table_suffix = k.split('_')[-1]  # get last element of string after _ to be table suffix
        if table_suffix not in table_meta_dictionary.keys():
            print(
                # skip unexpected table suffixes
                "Some table suffixes doesn't exist in table_names, probably autogenerated!?")
            continue
        result.append(
            E.tables(
                E.table(  # get tables
                    E.OutputFormat(
                        E.Columns(

                        ),
                        TableTitle="",
                        TableUniverse=""
                    ),
                    *get_variables(table_list[k], variable_description, meta_table_name)
                    ,
                    GUID=str(uuid.uuid4()),
                    VariablesAreExclusive='false',
                    DollarYear='0',
                    PercentBaseMin='1',
                    name=meta_table_name,
                    displayName=meta_table_name,
                    title=table_meta_dictionary[table_suffix],
                    titleWrapped=table_meta_dictionary[table_suffix],
                    universe='none',
                    Visible='true',
                    TreeNodeCollapsed='true',
                    CategoryPriorityOrder='0',
                    ShowOnFirstPageOfCategoryListing='false',
                    DbTableSuffix=table_suffix,
                    uniqueTableId=meta_table_name
                )
            )
        )

    return result


def get_geo_id_variables(geoLevelInfo):
    """
    Get variables (geography identifiers) from "Geography Summary File"
    :param geoLevelInfo: List from config file
    :return:
    """

    nesting_information = geoLevelInfo
    geo_table_field_list = [['QName', 'Qualifying Name', '2'], ['Name', 'Name of Area', '2'], ['FIPS', 'FIPS', '2']]
    # create additional variables
    [geo_table_field_list.append([i[1].upper(), i[1], '2']) for i in
     nesting_information]  # '2' means data type is string

    result = []
    E = ElementMaker()
    for i in geo_table_field_list:
        result.append(E.variable(
            GUID=str(uuid.uuid4()),
            UVID='',
            BracketSourceVarGUID='',
            BracketFromVal='0',
            BracketToVal='0',
            BracketType='None',
            FirstInBracketSet='false',
            notes='',
            PrivateNotes='',
            name=create_acronym(i[0]),
            label=i[1],
            qLabel='',
            indent='0',
            dataType=i[2],
            dataTypeLength='0',
            formatting='0',
            customFormatStr='',
            FormulaFunctionBodyCSharp='',
            suppType='0',
            SuppField='',
            suppFlags='',
            aggMethod='0',
            DocLinksAsString='',
            AggregationStr='None'
        )
        )
    return result


def get_geo_id_tables(geo_level_info):
    """
    Get table "Geography Identifiers" for "Geography Summary File"
    :param geo_level_info: List from config file
    :return:
    """
    # get_nesting_information = geo_level_info
    e = ElementMaker()
    result = [e.tables(
        e.table(
            e.OutputFormat(
                e.Columns(),
                TableTitle='',
                TableUniverse=''
            ),
            *get_geo_id_variables(geo_level_info),
            GUID=str(uuid.uuid4()),
            VariablesAreExclusive="false",
            notes="",
            PrivateNotes="",
            DollarYear="0",
            PercentBaseMin="1",
            name="G001",
            displayName="G1.",
            title="Geography Identifiers",
            titleWrapped="Geography Identifiers",
            titleShort="",
            universe="none",
            Visible="false",
            TreeNodeCollapsed="true",
            DocSectionLinks="",
            DataCategories="",
            ProductTags="",
            FilterRuleName="",
            CategoryPriorityOrder="0",
            ShowOnFirstPageOfCategoryListing="false",
            DbTableSuffix="001",
            uniqueTableId="G001",
            source="",
            DefaultColumnCaption="",
            samplingInfo=""
        )
    )]
    return result


# @profile
def create_metadata_xml(connection_string, server, dbname, project_name, project_year, metadata_file_name,
                        geo_level_info, project_id, variable_description, output_directory, user, password,
                        trusted_connection):
    e = ElementMaker()

    page = e.survey(
        e.Description(et.CDATA('')
                      ),
        e.notes(et.CDATA('')
                ),
        e.PrivateNotes(et.CDATA('')
                       ),
        e.documentation(
            e.documentlinks(
            ),
            Label='Documentation'
        ),
        e.geoTypes(
            *get_geotype(geo_level_info)
        ),
        e.GeoSurveyDataset(
            e.DataBibliographicInfo(

            ),
            e.notes(

            ),
            e.PrivateNotes(et.CDATA('')

                           ),
            e.Description(et.CDATA('')

                          ),
            e.datasets(
                *get_datasets(connection_string, dbname, geo_level_info, project_id, user, password, server,
                              trusted_connection)
            ),
            e.iterations(

            ),
            *get_geo_id_tables(geo_level_info),
            GUID=str(uuid.uuid4()),
            SurveyDatasetTreeNodeExpanded='true',
            TablesTreeNodeExpanded='true',
            IterationsTreeNodeExpanded='false',
            DatasetsTreeNodeExpanded='true',
            Description='Geographic Summary Count',
            Visible='false',
            abbreviation='Geo',
            name='Geography Summary File',
            DisplayName='Geography Summary File'
        ),
        e.SurveyDatasets(
            e.SurveyDataset(  # repeated for as many times as there are datasets
                e.DataBibliographicInfo(

                ),
                e.notes(

                ),
                e.PrivateNotes(
                    et.CDATA('')
                ),
                e.Description(
                    et.CDATA('')
                ),
                e.datasets(
                    *get_datasets(connection_string, dbname, geo_level_info, project_id, user, password, server,
                                  trusted_connection)
                ),
                e.iterations(

                ),
                e.tables(et.Comment("Insert SE tables here !!!"),

                         ),
                GUID=str(uuid.uuid4()),
                SurveyDatasetTreeNodeExpanded='true',
                TablesTreeNodeExpanded='true',
                IterationsTreeNodeExpanded='false',
                DatasetsTreeNodeExpanded='true',
                Description='',
                Visible='false',
                abbreviation='SE',
                name='Social Explorer Tables',
                DisplayName='Social Explorer Tables'
            ),
            e.SurveyDataset(  # repeated for as many times as there are datasets
                e.DataBibliographicInfo(

                ),
                e.notes(

                ),
                e.PrivateNotes(
                    et.CDATA('')
                ),
                e.Description(
                    et.CDATA('')
                ),
                e.datasets(
                    *get_datasets(connection_string, dbname, geo_level_info, project_id, user, password, server,
                                  trusted_connection)
                ),
                e.iterations(

                ),
                *get_tables(server, dbname, variable_description, user, password, project_year, trusted_connection),
                GUID=str(uuid.uuid4()),
                SurveyDatasetTreeNodeExpanded='true',
                TablesTreeNodeExpanded='true',
                IterationsTreeNodeExpanded='false',
                DatasetsTreeNodeExpanded='true',
                Description='',
                Visible='true',
                abbreviation='ORG',
                name='Original Tables',
                DisplayName='Original Tables'
            )
        ),
        e.Categories(
            e.string(
                project_name  # change into something more appropriate if possible
            )
        ),
        GUID=str(uuid.uuid4()),
        Visible='true',
        GeoTypeTreeNodeExpanded='true',
        GeoCorrespondenceTreeNodeExpanded='false',
        name=project_id,  # metadata_file_name, changed from project_name when meaning of project name changed
        DisplayName=project_name,
        year=project_year,
        Categories=''
    )
    tree = et.ElementTree(page)
    tree.write(output_directory + metadata_file_name)
    print("Writing to: ", output_directory + metadata_file_name)
    print("Everything finished successfully!!!")


def prepare_environment(config_file):
    """
    Initialize required variables and get information from config file
    :param config_file: Full path to config file
    :return:
    """

    # required for tables in metadata
    global tableCounter
    global variableCounter
    tableCounter = 0  # required for tables in metadata
    variableCounter = 0

    # take values from metadata file
    config = get_config(config_file)
    connection_string = config['connectionString']
    dbname = config['dbname']
    server = config['server']
    project_name = config['projectName']
    project_year = str(config['projectYear'])
    metadata_file_name = config['metadataFileName']
    geo_level_info = config['geoLevelInfo']
    project_id = config['projectId']
    variable_description_location = config['variableDescriptionLocation']
    output_directory = config['outputDirectory']
    user = config['user']
    password = config['password']
    trusted_connection = config['trustedConnection']

    if os.path.isfile(variable_description_location):
        variable_description = get_variable_descriptions_from_file(variable_description_location)
    else:
        variable_description = get_variable_descriptions_from_directory(variable_description_location)

    # check if there is proper number of columns in a file, maybe this could be moved to separate function?
    for v in variable_description.values():
        col_nr = len(v)
        if col_nr not in [1, 2]:
            print('Number of columns in variable description file/s is not ok!')
            sys.exit()

    col_nr_prev = [i for i in variable_description.values()]
    for i in variable_description.values():
        if len(i) != len(max(col_nr_prev, key=len)):
            print('Number of columns changes in the file!?')
            sys.exit()

    return [connection_string, server, dbname, project_name, project_year, metadata_file_name, geo_level_info,
            project_id, variable_description, output_directory, user, password, trusted_connection]


def verify_config(config_path_value):
    """
    Verify yml config file.
    :param config_path_value: Full path to config file
    :return: True if everything is OK
    """

    errors = []
    warnings = []
    if not os.path.isfile(config_path_value):
        print("Error: Config file doesn't exist on selected location: " + config_path_value + " !")
        return False

    config = get_config(config_path_value)
    if len(config['connectionString']) == 0 or 'connectionString' not in config.keys():
        errors.append('Error: Connection string not set properly in config file!')
    if len(config['projectName']) == 0 or 'projectName' not in config.keys():
        errors.append('Error: Project name not set properly in config file!')
    if len(config['projectId']) == 0 or 'projectId' not in config.keys():
        errors.append('Error: Project id not set properly in config file!')
    if type(config['projectDate']) is not datetime.date or 'projectDate' not in config.keys():
        errors.append('Error: Project date not set properly in config file!')
    if len(config['dbname']) == 0 or 'dbname' not in config.keys():
        errors.append('Error: Database name not set properly in config file!')
    if len(config['server']) == 0 or 'server' not in config.keys():
        errors.append('Error: Server name not set properly in config file!')
    if len(config['user']) == 0 or 'user' not in config.keys():
        errors.append('Error: User name not set properly in config file!')
    if len(str(config['projectYear'])) != 4 or 'projectYear' not in config.keys():
        errors.append('Error: Project year not set properly in config file!')
    if config['projectYear'] > datetime.datetime.now().year:
        warnings.append('Warning: Project year is set in future.')
    if (not (
                os.path.isfile(config['variableDescriptionLocation']) or os.path.isdir(
                    config['variableDescriptionLocation']))):
        errors.append('Error: Something is wrong with variable info location!')

    for warn in warnings:
        print(warn)

    if len(errors) == 0:
        return True
    else:
        for err in errors:
            print(err)
        return False


def menu():
    """
    Display menu and pass command line parameters.
    :return: Options object with values from cmd
    """
    usage = "%prog -c arg"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-c', '--config-file', dest='configFilePath', help='Full path to the config file!',
                      metavar='configFilePath')
    (options, args) = parser.parse_args()
    return options


if __name__ == '__main__':
    opt = menu()
    if len(argv) == 1:
        config_path = 'config.yml'
    else:
        config_path = opt.configFilePath

    if verify_config(config_path):
        create_metadata_xml(*prepare_environment(config_path))
