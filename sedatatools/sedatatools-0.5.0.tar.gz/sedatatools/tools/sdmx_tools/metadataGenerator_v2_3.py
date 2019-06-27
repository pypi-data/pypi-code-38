"""
This script will generate metadata file
v2.3
"""

from lxml import etree as ET
from lxml.builder import ElementMaker
import uuid
import pymssql
import csv
import os
import yaml
import sys
import collections # used for dictionary sorting
import datetime # used for validation
import optparse
from sys import argv

def getTableFipses(tableFips, geoLevelInfo):
    """
    This will create a string with list of FIPS columns (SL050_FIPS, SL040_FIPS, etc.) based on nesting information (DB Conn. Info)
    :param tableFips: Fips code for the geo that table is on e.g. for county level table it's FIPS_SL050
    :param geoLevelInfo: GeoInfo from config file
    :return: String with list of FIPS columns
    """
    # this list should always return just one element, if not then sumlevs are not unique
    lowFipsPos = [i for i, k in enumerate(geoLevelInfo) if k[0] == tableFips.replace('_FIPS','') ][0]
    fullFipsList = [tableFips]
    for i in reversed(range(lowFipsPos)):
        fullFipsList.append(geoLevelInfo[i][0] +'_FIPS')
        if geoLevelInfo[i][4] == 0:
            break
    fullFipsList = ','.join(fullFipsList)
    return fullFipsList

def getConfig(configFile):
    with open(configFile,'r') as conf:
        config = yaml.load(conf)
    return config


def createAcronym(string):
    """
    Create acronym from a multiworld string, in case only one word is in string it will capitalize it.
    :param string: String to create acronym from
    :return:
    """
    charsForRemoval = ['(',')','&','/',',','.','\\','\'','&','%','#']
    for ch in charsForRemoval:
        if ch in string:
            string = string.replace(ch,' ')
    string = string.strip()
    while('  ' in string):
        string = string.replace('  ',' ')
    if ' ' in string:
        blankPos = [i for i, letter in enumerate(string) if letter == ' ']
        acronym =string[0] + ''.join([string[i+1] for i in blankPos]).upper()
    else:
        acronym = string.upper()
    return acronym


def getTableMetadataFromDb(server, dbname, user, password, projectYear):
    """
    Get table descriptions from table_names table in database, make it prettier and return it as a dictionary
    :param server: Server address
    :param dbname: Database names
    :return: Dictionary of metadata tables
    """
    extension = ['.txt','.csv','.tsv'] # extensions to remove from input file e.g. Sex_by_Age.csv > Sex_by_Age
    metaTableDictionary = {}

    conn = pymssql.connect(host = server, database = dbname)
    #conn = pymssql.connect(host = server, database = dbname, user = user, password = password)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM table_names where projectYear = ' + projectYear)
    tableNames = cursor.fetchall()

    # exit if table_names table empty
    if len(tableNames) == 0:
        print("Error: Table names does not exist in database!")
        sys.exit()

    metaData = []
    for ext in extension:
        for el in tableNames: # TODO this will create problem if there's no extension in file name, it will break!!!
            if ext in el[0]:
                metaData.append([el[0].replace(ext, '')[el[0].index('_')+1:],el[1]]) # remove extension and dataset ID (everything until first '_')

    for i in metaData:
        metaTableDictionary[i[1]] = i[0].replace('_',' ')

    return metaTableDictionary

def checkDataType(datum):
    """
    This function checks type of value because pymssql cannot distinguish int from float
    :param datum: Value to be checked
    :return:
    """
    if isinstance(datum,int):
        return 3
    elif isinstance(datum,float):
        return 2
    elif isinstance(datum,str):
        return 1
    elif datum == None:
        return 9
    else:
        print("Undefined data type in source data for: ", datum) # if nothing then string

def getTablesFromDb(server, dbname, multipleYearsInDb, projectYear, user, password): # TODO DONE
    """
    Get list of tables from db, make it unique on metadata level and return it as a dictionary
    :param server:
    :param dbname:
    :return:
    """
    conn = pymssql.connect(server = server, database = dbname) # for trusted connection
    #conn = pymssql.connect(host = server, database = dbname, user = user, password = password )
    cursor = conn.cursor()

    if multipleYearsInDb == True:
        cursor.execute("SELECT name FROM sys.objects WHERE type_desc = 'USER_TABLE' AND name <> 'table_names' and left(name,1) <> '_' and name like '%" + str(projectYear) + "%' ORDER BY modify_date")
    else:
        cursor.execute("""
        SELECT name
        FROM sys.objects
        WHERE type_desc = 'USER_TABLE'
        AND name <> 'table_names'
        AND left(name,1) <> '_'
        AND name <> 'sysdiagrams'
        ORDER BY modify_date
        """)

    tableList = [str(*i) for i in cursor.fetchall() if i != 'table_names']
    dictTablesAndVars = {}
    cursor = conn.cursor()
    for i in tableList:
        sql = 'SELECT * FROM ' + i
        cursor.execute(sql)
        varTypes = [checkDataType(j) for k in cursor for j in k]
        dictTablesAndVars[i] = [j[0] for j in cursor.description]
        attribType = [j[1] for j in cursor.description]
        dictTablesAndVars[i] = list(zip(dictTablesAndVars[i],varTypes, attribType))
    conn.close()

    dictTablesAndVarsUnique = {}
    for key,value in dictTablesAndVars.items():
        values = []
        posT = [i for i,k in enumerate(key) if k == '_'][1]+1
        for v in value:
            # skip system required names
            if len([j for j,l in enumerate(v[0]) if l == '_']) < 3: # TODO create check and warning for this before loop
                continue
            posV = [j for j,l in enumerate(v[0]) if l == '_'][2]+1
            # print(key[posT:])
            # print(v[0][posV:])
            values.append([v[0][posV:],v[1]])
        dictTablesAndVarsUnique[key[posT:]] = values

    return dictTablesAndVars


def getVariableDescriptionsFromFile(variableDescriptionLocation):
    """
    Open file and read variable names and its description. Files must be in format: variable_id, description
    :param variableDescriptionLocation: Full path to the file
    :return: Dictionary with variable id as key and its description as a value
    """
    fileContentDict = {}
    with open(variableDescriptionLocation) as file:
        reader = csv.reader(file)
        for var in list(reader):
            fileContentDict[var[0]] = var[1]
    return fileContentDict


def getVariableDescriptionsFromDirectory(variableDescriptionLocation):
    """
    In case folder is provided, take a list of its files and read it vor variable description
    :param variableDescriptionLocation: Full path to the folder with files
    :return: Dictionary with variable id as key and its description as a value
    """
    os.chdir(variableDescriptionLocation)
    fileList = os.listdir()
    fileContentDict = {}
    for fileName in fileList:
        fileContentDict.update(getVariableDescriptionsFromFile(fileName))
    return fileContentDict


def getGeotype(geoLevelInfo): # number of geotypes
    """
    Get list of geotypes in project
    :param geoLevelInfo: List from config file
    :return:
    """
    E = ElementMaker()
    sumLevs = geoLevelInfo # getGeoNesting(geoLevelInfoFilePath)
    pluralForms = {'County':'Counties','State':'States'}
    for i in sumLevs:
        if i[1] not in sumLevs:
            pluralForms[i[1]] = i[1]

    # create names of relevant geos
    relevantGeos = ','.join([createAcronym(i[1]) for i in sumLevs])

    result = []
    # # create first level to hold all other nesting TODO check if it is really necessary, no its not, delete after testing
    # result = [(E.geoType(E.Visible('true'),
    # GUID = str(uuid.uuid4()),
    # Name = 'World',
    # Label = 'World',
    # QLabel = 'World',
    # RelevantGeoIDs = 'FIPS,NAME,QName,' + relevantGeos,
    # PluralName = 'World',
    # fullCoverage = 'false',
    # majorGeo = 'false',
    # #GeoAbrev = sumlev[0],#'us, nation', COMMENTED BECAUSE IN ACS 2011 EXAMPLE IT WAS MISSING!?
    # Indent = '0',
    # Sumlev = '000',
    # FipsCodeLength = '0',
    # FipsCodeFieldName = 'FIPS',
    # FipsCodePartialFieldName = '',
    # FipsCodePartialLength = '0')
    # )]

    for sumlev in sumLevs:
        partialFipsField = createAcronym(sumlev[1])
        result.append(E.geoType(E.Visible('true'),
        GUID = str(uuid.uuid4()),
        Name = sumlev[0],
        Label = sumlev[1],
        QLabel = sumlev[1],
        RelevantGeoIDs = 'FIPS,NAME,QName,' + relevantGeos,
        PluralName = pluralForms[sumlev[1]],
        fullCoverage = 'true',
        majorGeo = 'true',
        #GeoAbrev = sumlev[0],#'us, nation', COMMENTED BECAUSE IN ACS 2011 EXAMPLE IT WAS MISSING!?
        Indent = str(int(sumlev[4])),
        Sumlev = sumlev[0].replace('SL',''),
        FipsCodeLength = sumlev[2],
        FipsCodeFieldName = 'FIPS',
        FipsCodePartialFieldName = partialFipsField,
        FipsCodePartialLength = str(sumlev[3]))
        )
    return result


def getDatasets(connectionString, dbname, geoLevelInfo, projectId, user, password, server):
    """
    Get data sets for the project.
    :param connectionString: Info from config file
    :param dbname: Info from config file
    :param geoLevelInfo: Info from config file
    :param projectId: Info from config file
    :param user: Info from config file
    :param password: Info from config file
    :param server: Info from config file
    :return: List of data sets
    """
    E = ElementMaker()
    result = []

    sumLevs = geoLevelInfo
    for i in sumLevs:
        geoIdSuffix = getGeoIdDbTableName(i[0], dbname, user, password, server, projectId)

        result.append(E.dataset(GUID = str(uuid.uuid4()),
        GeoTypeName = i[0], # SL040
        DbConnString = connectionString,
        DbName = dbname,
        GeoIdDbTableName = projectId + '_' + i[0] + geoIdSuffix, # tablename e.g. 'LEIP1912_SL040_PRES_001'
        IsCached = 'false',
        DbTableNamePrefix = projectId + '_' + i[0] + '_', # tablename prefix e.g. 'LEIP1912_SL040_PRES_'
        DbPrimaryKey = getTableFipses(i[0]+'_FIPS',geoLevelInfo), # this is fixed
        DbCopyCount = '1'))
    return result

def getGeoIdDbTableName(sumlev, dbname, user, password, server, projectId):
    """
    Find suffix of first table for specific geography and return it together with preceding '_'.

    :param sumlev: Summary level for which it is neccessary to find suffix
    :param dbname: Database name
    :param user: Username
    :param password: Password
    :param server: Server name
    :return: Suffix off the first geography for that table
    """
    # for trusted connecttion
    conn = pymssql.connect(host = server, database = dbname)
    #conn = pymssql.connect(host = server, database = dbname, user = user, password = password )
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 name FROM sys.objects WHERE type_desc = 'USER_TABLE' AND name <> 'table_names' and left(name,1) <> '_' and name like '%" + sumlev + "%' and name like '" + projectId + "%' ORDER BY name")
    tableName = cursor.fetchall()
    if not tableName: # this is fix for sumlevels that doesn't exist in database, remove this after cancen is done
        return '_001'
    tableName = tableName[0][0]
    suffixInd = [index for index, element in enumerate(tableName) if element == '_'][-1]
    suffix = tableName[suffixInd:]
    return suffix

def getVariables(variables, variableDescription, metaTableName):
    """
    Get variables for original tables
    :param variables: List of variables
    :param variableDescription: List of variable descriptions
    :param metaTableName: Table name for metadata file, extracted from data file name
    :return:
    """
    result = []
    E = ElementMaker()
    # remove unwanted variables
    removalVars = ['NAME', 'SUMLEV', 'v1', 'Geo_level', 'QName', 'TYPE', 'Geo', 'FIPS', 'Geo_orig']
    variables = [i for i in variables if i[0] not in removalVars]
    variables = [i for i in variables if '_NAME' not in i[0] and 'FIPS' not in i[0] and 'V1' != i[0]]

    for i in variables:
        #create variable Id's for metadata as metaTableName + variable order
        global variableCounter
        variableCounter += 1
        metaVariableName = metaTableName + str(100000 + variableCounter)[-5:]

        #position after project name, sumlev, and order number, needed for variable description
        if len([index for index, chr in enumerate(i[0]) if chr == '_']) == 0:
            continue
        pos = [index for index, chr in enumerate(i[0]) if chr == '_'][1] + 1

        # create variable type
        if i[1] == 3: # integer
            varType = '4'
            formatingValue = '9' # 1,234
        elif i[1] == 2:
            varType = '7'
            formatingValue = '9' # 1,234
        elif i[1] == 1: # char
            varType = '2'
            formatingValue = '0' # none
        elif i[1] == 9 and i[2] == 3: # none
            varType = '7'
            formatingValue = '9' # 1,234
        elif i[1] == 9 and i[2] == 1:
            varType = '2'
            formatingValue = '0' # none
        else:
            varType = '0'
            formatingValue = '0'

        # in case unexpected variable name appear in table, print warning and skip it
        if i[0][pos:] not in  variableDescription.keys(): # check if range exists because it searches for the variables that doesn't exists
            print("Warning: Undefined variable found:",i[0], i[0][pos:])
            continue

        result.append(E.variable( # repeated for as many times as there are variables
        GUID = str(uuid.uuid4()),
        UVID='',
        BracketSourceVarGUID='',
        BracketFromVal = '0',
        BracketToVal = '0',
        BracketType = 'None',
        FirstInBracketSet = 'false',
        notes ='',
        PrivateNotes='',
        name =  i[0], # metaVariableName
        label = variableDescription[i[0][pos:]], # find variable description in dictionary, by text after pr. id and order
        qLabel='',
        indent = '0',
        dataType = varType,
        dataTypeLength = '0',# default to zero
        formatting = formatingValue, # TODO check whats this, probably 9 for dt 4, 0 for 2
        customFormatStr='', # only for SE tables
        FormulaFunctionBodyCSharp='',# only for SE tables
        suppType = '0',
        SuppField='',
        suppFlags='',
        aggMethod = '1',
        DocLinksAsString='',
        AggregationStr = 'Add'#'None'
            )
    )
    return result


def getTables(server, dbname, variableDescription, user, password, multipleYearsInDb, projectYear):
    """
    Get list of original tables from db
    :param server: Server name
    :param dbname: Database name
    :param variableDescription: List to decode variable names into descriptions (from variable_descriptions file)
    :param user: Username for server
    :param password: Password for server
    :param multipleYearsInDb: Flag if there is multiple years in single database #TODO  remove this when corrected
    :param projectYear: Project year
    :return: list with constructed tables tags
    """
    tableList = getTablesFromDb(server, dbname, multipleYearsInDb, projectYear, user, password)
    tableList = collections.OrderedDict(sorted(tableList.items()))
    tableMetaDictionary = getTableMetadataFromDb(server, dbname, user, password, projectYear)
    E = ElementMaker()
    result = []
    duplicationCheckList = []

    for k,v in tableList.items():

        cutPos = [i for i,el in enumerate(k) if el == '_']

        if (k[:cutPos[0]] + k [cutPos[-1]+1:]) in duplicationCheckList: # if table is already added, skipp it
            continue

        duplicationCheckList.append(
            k[:cutPos[0]] + k [cutPos[-1]+1:]
        )
        # create table ID's for metadata
        global tableCounter
        tableCounter += 1
        metaTableName = k[:cutPos[0]] + '_' + k [cutPos[-1]+1:] # this defines how table Id will be presented in metadata
        tableSuffix = k.split('_')[-1] # get last element of string after _ to be table suffix
        if tableSuffix not in tableMetaDictionary.keys():
            print("Some table suffixes doesn't exist in table_names, probably autogenerated!?") # skip unexpected table suffixes
            continue
        result.append(
        E.tables(
          E.table( # get tables
            E.OutputFormat(
              E.Columns (

              ),
            TableTitle="",
            TableUniverse=""
            ),
              *getVariables(tableList[k], variableDescription, metaTableName)
            ,
              GUID = str(uuid.uuid4()),
              VariablesAreExclusive = 'false',
              DollarYear = '0',
              PercentBaseMin = '1',
              name = metaTableName,
              displayName = metaTableName,
              title = tableMetaDictionary[tableSuffix],
              titleWrapped =  tableMetaDictionary[tableSuffix],
              universe  ='none',
              Visible = 'true',
              TreeNodeCollapsed = 'true',
              CategoryPriorityOrder = '0',
              ShowOnFirstPageOfCategoryListing = 'false',
              DbTableSuffix = tableSuffix,
              uniqueTableId = metaTableName
              )
            )
        )

    return  result


def getGeoIdVariables(geoLevelInfo):
    """
    Get variables (geography identifiers) from "Geography Summary File"
    :param geoLevelInfo: List from config file
    :return:
    """

    nestingInformation = geoLevelInfo #getGeoNesting(geoLevelInfoFilePath)
    geoTableFieldList = [['QName','Qualifying Name','2'],['Name','Name of Area', '2'],['FIPS','FIPS', '2']]
    # create additional variables
    [geoTableFieldList.append([i[1].upper(), i[1], '2']) for i in nestingInformation] # '2' means data type is string

    result = []
    E = ElementMaker()
    for i in geoTableFieldList:
        result.append(E.variable(
            GUID= str(uuid.uuid4()),
            UVID='',
            BracketSourceVarGUID='',
            BracketFromVal='0',
            BracketToVal='0',
            BracketType='None',
            FirstInBracketSet='false',
            notes='',
            PrivateNotes='',
            name=createAcronym(i[0]),
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


def getGeoIdTables(geoLevelInfo):
    """
    Get table "Geography Identifiers" for "Geography Summary File"
    :param geoLevelInfo: List from config file
    :return:
    """
    getNestingInformation = geoLevelInfo #getGeoNesting(geoLevelInfoFilePath)
    E = ElementMaker()
    result = []
    result.append(E.tables(
        E.table(
            E.OutputFormat(
                E.Columns(),
                TableTitle = '',
                TableUniverse = ''
            ),
            *getGeoIdVariables(geoLevelInfo),
            GUID = str(uuid.uuid4()),
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
    )
    )
    return result

#@profile
def createMetadataXML(connectionString, server, dbname,projectName, projectYear, metadataFileName, geoLevelInfo, projectId, variableDescription, outputDirectory, user, password, multipleYearsInDb):

    E = ElementMaker()

    page = E.survey(
      E.Description(ET.CDATA('')
      ),
      E.notes (ET.CDATA('')
      ),
      E.PrivateNotes (ET.CDATA('')
      ),
      E.documentation (
        E.documentlinks(
        ),
          Label = 'Documentation'
      ),
      E.geoTypes (
          *getGeotype(geoLevelInfo)
      ),
      E.GeoSurveyDataset(
        E.DataBibliographicInfo (

        ),
        E.notes (

        ),
        E.PrivateNotes(ET.CDATA('')

        ),
        E.Description(ET.CDATA('')

        ),
        E.datasets(
          *getDatasets(connectionString, dbname, geoLevelInfo, projectId, user, password, server)
        ),
        E.iterations (

        ),
        *getGeoIdTables(geoLevelInfo),
          GUID = str(uuid.uuid4()),
          SurveyDatasetTreeNodeExpanded = 'true',
          TablesTreeNodeExpanded = 'true',
          IterationsTreeNodeExpanded = 'false',
          DatasetsTreeNodeExpanded = 'true',
          Description = 'Geographic Summary Count',
          Visible = 'false',
          abbreviation = 'Geo',
          name = 'Geography Summary File',
          DisplayName = 'Geography Summary File'
      ),
        E.SurveyDatasets(
          E.SurveyDataset( # repeated for as many times as there are datasets
            E.DataBibliographicInfo(

            ),
            E.notes(

            ),
            E.PrivateNotes(
                ET.CDATA('')
            ),
            E.Description(
                ET.CDATA('')
            ),
            E.datasets(
                *getDatasets(connectionString, dbname, geoLevelInfo,projectId,user, password, server)
            ),
            E.iterations(

            ),
          E.tables(ET.Comment("Insert SE tables here !!!"),

            ),
          GUID = str(uuid.uuid4()),
          SurveyDatasetTreeNodeExpanded = 'true',
          TablesTreeNodeExpanded = 'true',
          IterationsTreeNodeExpanded = 'false',
          DatasetsTreeNodeExpanded = 'true',
          Description = '',
          Visible = 'false',
          abbreviation = 'SE',
          name = 'Social Explorer Tables',
          DisplayName = 'Social Explorer Tables'
          ),
        E.SurveyDataset( # repeated for as many times as there are datasets
            E.DataBibliographicInfo(

            ),
            E.notes(

            ),
            E.PrivateNotes(
                ET.CDATA('')
            ),
            E.Description(
                ET.CDATA('')
            ),
            E.datasets(
                *getDatasets(connectionString, dbname, geoLevelInfo, projectId, user, password, server)
            ),
            E.iterations(

            ),
        *getTables(server, dbname, variableDescription, user, password, multipleYearsInDb, projectYear),
          GUID = str(uuid.uuid4()),
          SurveyDatasetTreeNodeExpanded = 'true',
          TablesTreeNodeExpanded = 'true',
          IterationsTreeNodeExpanded = 'false',
          DatasetsTreeNodeExpanded = 'true',
          Description = '',
          Visible = 'true',
          abbreviation = 'ORG',
          name = 'Original Tables',
          DisplayName = 'Original Tables'
          )
         ),
        E.Categories(
            E.string(
                projectName # change into somethin more appropriate if possible
            )
        ),
          GUID = str(uuid.uuid4()),
          Visible = 'true',
          GeoTypeTreeNodeExpanded = 'true',
          GeoCorrespondenceTreeNodeExpanded = 'false',
          name = projectId,#metadataFileName, changed from projectName when meaning of project name changed
          DisplayName = projectName,
          year = projectYear,
          Categories = ''
    )
    tree = ET.ElementTree(page)
    tree.write(outputDirectory + metadataFileName)
    print("Writing to: ",outputDirectory + metadataFileName)
    print("Everything finished succesfully!!!")

def prepareEnvironment(configFile):
    """
    Initialize required variables and get information from config file
    :param configFile: Full path to config file
    :return:
    """

    # required for tables in metadata
    global tableCounter
    global variableCounter
    tableCounter = 0 # required for tables in metadata
    variableCounter = 0

    # take values from metadata file
    config = getConfig(configFile)
    connectionString = config['connectionString']
    dbname = config['dbname']
    server = config['server']
    projectName = config['projectName']
    projectYear = str(config['projectYear'])
    metadataFileName = config['metadataFileName']
    geoLevelInfo = config['geoLevelInfo']
    projectId = config['projectId']
    variableDescriptionLocation = config['variableDescriptionLocation']
    outputDirectory = config['outputDirectory']
    user = config['user']
    password = config['password']
    if 'multipleYearsInDb' in config.keys():
        multipleYearsInDb = config['multipleYearsInDb']
    else:
        multipleYearsInDb = False
    if os.path.isfile(variableDescriptionLocation):
        variableDescription = getVariableDescriptionsFromFile(variableDescriptionLocation)
    elif os.path.isdir(variableDescriptionLocation):
        variableDescription = getVariableDescriptionsFromDirectory(variableDescriptionLocation)
    else:
        print("Error: Something is wrong with variable info location!")
        sys.exit()
    return [connectionString, server,dbname, projectName, projectYear, metadataFileName, geoLevelInfo, projectId, variableDescription, outputDirectory, user, password, multipleYearsInDb]


def verifyConfig(configPath):
    """
    Verify yml config file.
    :param configPath: Full path to config file
    :return: True if everything is OK
    """

    errors = []
    warnings = []
    if not os.path.isfile(configPath):
        print("Config file doesn't exist on selected location: "+configPath +" !")
        return False

    config = getConfig(configPath)
    if len(config['connectionString'])== 0  or 'connectionString' not in config.keys():
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
    if len(str(config['projectYear'])) != 4  or 'projectYear' not in config.keys():
        errors.append('Error: Project year not set properly in config file!')
    if config['projectYear'] > datetime.datetime.now().year:
        warnings.append('Warning: Project year is set in future.')

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
    parser.add_option('-c', '--config-file', dest = 'configFilePath', help='Full path to the config file!', metavar='configFilePath')
    (options, args) = parser.parse_args()
    return options

if __name__ == '__main__':
    opt = menu()
    if len(argv) == 1:
        configPath = 'C:/Projects/ContentProduction/Canadian Census/scripts/postprocessing - R/config.yml'
    else:
        configPath = opt.configFilePath

    if verifyConfig(configPath):
        createMetadataXML(*prepareEnvironment(configPath))
    #'C:/Projects/ContentProduction/Canadian Census/scripts/postprocessing - R/config.yml'
     #'z:/NYC_CITYPLAN/Scripts/config_city_plan_2015.yml'
    #  for yr in range(2012,2013):
    #      print('Processing year ' + str(yr))
    #      createMetadataXML(*prepareEnvironment('Z:/CDCHealth/HealthAll/'+ str(yr) + '/config_edo_'+ str(yr) +'.yml'))
    # #Z:/CDCHealth/HealthAll.old/2015/config_edo_2015.yml
    #C:/Projects/ContentProduction/Canadian Census/scripts/postprocessing - R/config.yml
    #'z:/NYC_CITYPLAN/Scripts/config_city_plan_2015.yml'
    #createMetadataXML(*prepareEnvironment('Z:/CDCHealth/HealthAll/2015/config_edo_2015.yml'))
    #Z:/eurostat/2010/config_eurostat.yml


    #'C:/Projects/ContentProduction/Canadian Census/scripts/postprocessing - R/config.yml'

