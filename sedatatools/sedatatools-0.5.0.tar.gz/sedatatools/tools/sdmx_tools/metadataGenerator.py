"""
This script will generate metadata for canadian census project
"""

from lxml import etree as ET
from lxml.builder import ElementMaker
import uuid
import pymssql
import csv
import yaml

class config():
    def __init__(self, connectionString, dbname, server, projectName, projectYear, metadataFileName, geoLevelInfoFilePath, tablePrefixName):
        self.connectionString = connectionString
        self.dbname = dbname
        self.server = server
        self.projectName = projectName
        self.projectYear = projectYear
        self.metadataFileName = metadataFileName
        self.geoLevelInfoFilePath = geoLevelInfoFilePath
        self.tablePrefixName = tablePrefixName


def getTablesFromDb(server, dbname): # TODO DONE
    conn = pymssql.connect(host = server, database = dbname)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT name
    FROM sys.objects
    WHERE type_desc = 'USER_TABLE'
    ORDER BY modify_date
    """)
    tableList = [str(*i) for i in cursor.fetchall() if i != 'table_names']
    dictTablesAndVars = {}
    cursor = conn.cursor()
    for i in tableList:
        sql = 'SELECT * FROM ' + i
        cursor.execute(sql)
        dictTablesAndVars[i] = [[i[0],type(i[1])] for i in cursor.description]
    conn.close()
    return dictTablesAndVars
    # return {'test':[['T001','T001Label','0','2','50','0','0','0','None'],['T002','T002Label','0','2','50','0','0','0','None']]}
#
# def getSumlevs(): # TODO removethis , old function that returned only fips and name , replaced with getGeoNesting()
#     file = open('Z:/Canadian Census/postprocessing/test_external_data_source/edo/all_geotypes_and_sumLev.csv')
#     fileContent = file.read()
#     fileContent = [i.split(',')for i in fileContent.split('\n')][1:] # return list without header
#     fileContent = [i for i in fileContent if len(i) != 1 ] # remove emtpy elements if any
#     sumLevs = set([i[2] +','+ i[3]+','+str(len(i[0])) for i in fileContent])
#     sumLevs = [i.split(',') for i in sumLevs]
#     return sumLevs

def getGeoNesting(geoLevelInfoFilePath): # TODO DONE
    with open(geoLevelInfoFilePath) as file:
        reader = csv.reader(file)
        fileContent = list(reader)
    return fileContent[1:]


def getGeotype(geoLevelInfoFilePath): # number of geotypes # TODO DONE
    E = ElementMaker()
    sumLevs = getGeoNesting(geoLevelInfoFilePath)
    pluralForms = {'County':'Counties','State':'States'}
    result = []
    for sumlev in sumLevs:
        # result.append(E()) EXAMPLE
        result.append(E.geoType(E.Visible('true'),
        GUID = str(uuid.uuid4()),
        Name = sumlev[1],
        Label = sumlev[1],
        QLabel = sumlev[1],
        RelevantGeoIDs = 'FIPS,NAME,QName',
        PluralName = pluralForms[sumlev[1]],
        fullCoverage = 'false',
        majorGeo = 'false',
        GeoAbrev = sumlev[0],#'us, nation',
        Indent = sumlev[4],
        Sumlev = sumlev[0].replace('SL',''),
        FipsCodeLength = sumlev[2],
        FipsCodeFieldName = 'FIPS',
        FipsCodePartialLength = sumlev[3])
        )

    return result

def getDatasets(connectionString, dbname, geoLevelInfoFilePath, tablePrefixName):  # TODO DONE
    E = ElementMaker()
    result = []
    sumLevs = getGeoNesting(geoLevelInfoFilePath)
    for i in sumLevs:
        result.append(E.dataset(GUID = str(uuid.uuid4()),
        GeoTypeName = i[1], # SL040
        DbConnString = connectionString,
        DbName = dbname,
        GeoIdDbTableName = i[1] + '_001', # tablename e.g. 'LEIP1912_SL040_PRES_001'
        IsCached = 'false',
        DbTableNamePrefix = tablePrefixName + i[1] + '_', # tablename prefix e.g. 'LEIP1912_SL040_PRES_'
        DbPrimaryKey = i[1]+'_FIPS', # this is fixed
        DbCopyCount = '1'))
    return result

def getVariables(variables):
    # variables = name, label, indent, dataType, dataTypeLength, formatting, suppType, aggMethod, AggregationStr
    result = []
    E = ElementMaker()
    for i in variables:
        if i[1] is int:
            varType = '4'
            formatingValue = '9' # 1,234
        elif i[1] is float:
            varType = '7'
            formatingValue = '9' # 1,234
        elif i[1] is str:
            varType = '2'
            formatingValue = '0' # none
        else:
            varType = '0'
            formatingValue = '0'

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
        name = i[0],
        label = i[0],
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


def getTables(server, dbname):
    tableList = getTablesFromDb(server, dbname)
    E = ElementMaker()
    result = []
    for k,v in tableList.items():
        tableSuffix = k[0].split('_')[-1] # get last element of string after _ to be table suffix
        result.append(
        E.tables(
          E.table( # get tables
            E.Outputformat(
              E.columns (

              ),
            TableTitle="",
            TableUniverse=""
            ),
              *getVariables(tableList[k])
            ,
              GUID = str(uuid.uuid4()),
              VariablesAreExclusive = 'false',
              DollarYear = '0',
              PercentBaseMin = '1',
              name = k,
              displayName = k,
              title = 'Geography Identifiers', # TODO get this from table metadata file
              titleWrapped = 'Geography Identifiers',# TODO get this from table metadata file
              universe  ='none',
              Visible = 'false',
              TreeNodeCollapsed = 'true',
              CategoryPriorityOrder = '0',
              ShowOnFirstPageOfCategoryListing = 'false',
              DbTableSuffix = tableSuffix,
              uniqueTableId = k
          )
        )
        )
    return  result


def getGeoIdVariables(geoLevelInfoFilePath):
    nestingInformation = getGeoNesting(geoLevelInfoFilePath)
    geoTableFieldList = [['QName','Qualifying Name','2'],['Name','Name of Area', '2'],['FIPS','FIPS', '2']]
    [geoTableFieldList.append([i[1].upper(), i[1], '3']) for i in nestingInformation]
    [geoTableFieldList.append([i[0] + '_FIPS', i[1], '3']) for i in nestingInformation]
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
            name=i[0],
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


def getGeoIdTables(geoLevelInfoFilePath):
    getNestingInformation = getGeoNesting(geoLevelInfoFilePath)
    E = ElementMaker()
    result = []
    result.append(E.tables(
        E.table(
            E.OutputFormat(
                E.Columns(),
                TableTitle = '',
                TableUniverse = ''
            ),
            *getGeoIdVariables(geoLevelInfoFilePath),
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


def main(connectionString, server, dbname,projectName, projectYear, metadataFileName, geoLevelInformation, tablePrefixName):

    E = ElementMaker()#namespace= 'http://www.w3.org/2001/XMLSchema-instance', nsmap = {'p' : "http://www.w3.org/2001/XMLSchema"})

    page = E.survey(
      E.description(ET.CDATA('')
      ),
      E.notes (ET.CDATA('')
      ),
      E.privatenotes (ET.CDATA('')
      ),
      E.documentation (
        E.documentlinks(
        ),
          Label = 'Documentation'
      ),
      E.geoTypes (
          *getGeotype(geoLevelInformation)
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
          *getDatasets(connectionString, dbname, geoLevelInfoFilePath, tablePrefixName)
        ),
        E.iterations (

        ),
        *getGeoIdTables(geoLevelInfoFilePath),
          GUID = str(uuid.uuid4()),
          SurveyDatasetTreeNodeExpanded = 'true',
          TablesTreeNodeExpanded = 'true',
          IterationsTreeNodeExpanded = 'false',
          DatasetsTreeNodeExpanded = 'true',
          description = 'Geographic Summary Count',
          Visible = 'false',
          abbreviation = 'Geo',
          name = 'Geography Summary File',
          DisplayName = 'Geography Summary File'
      ),
        E.surveydatasets(
          E.surveydataset( # repeated for as many times as there are datasets
            E.databibliographicinfo(

            ),
            E.notes(

            ),
            E.privatenotes(
                ET.CDATA('')
            ),
            E.description(
                ET.CDATA('')
            ),
            E.datasets(
                *getDatasets(connectionString, dbname, geoLevelInfoFilePath ,tablePrefixName)
            ),
            E.iterations(

            ),
        #*getTables(server, dbname), # for social explorer tables don't use tables from DB
          GUID = str(uuid.uuid4()),
          SurveyDatasetTreeNodeExpanded = 'true',
          TablesTreeNodeExpanded = 'true',
          IterationsTreeNodeExpanded = 'false',
          DatasetsTreeNodeExpanded = 'true',
          description = '',
          Visible = 'false',
          abbreviation = 'SE',
          name = 'Social Explorer Tables',
          DisplayName = 'Social Explorer Tables'
          ),
        E.surveydataset( # repeated for as many times as there are datasets
            E.databibliographicinfo(

            ),
            E.notes(

            ),
            E.privatenotes(
                ET.CDATA('')
            ),
            E.description(
                ET.CDATA('')
            ),
            E.datasets(
                *getDatasets(connectionString, dbname, geoLevelInfoFilePath, tablePrefixName)
            ),
            E.iterations(

            ),
        *getTables(server, dbname),
          GUID = str(uuid.uuid4()),
          SurveyDatasetTreeNodeExpanded = 'true',
          TablesTreeNodeExpanded = 'true',
          IterationsTreeNodeExpanded = 'false',
          DatasetsTreeNodeExpanded = 'true',
          description = '',
          Visible = 'false',
          abbreviation = 'ORG',
          name = 'Original Tables',
          DisplayName = 'Original Tables'
          )
         ),
        E.categories(
            E.string(
                projectName
            )
        ),
          GUID = str(uuid.uuid4()),
          Visible = 'true',
          GeoTypeTreeNodeExpanded = 'true',
          GeoCorrespondenceTreeNodeExpanded = 'false',
          name = metadataFileName,
          DisplayName = projectName,
          year = projectYear,
          Categories = 'Presidential Elections;'
    )
    print(ET.tostring(page, pretty_print=True, xml_declaration=True, encoding="utf-8"))
    tree = ET.ElementTree(page)
    tree.write('xmlMetadataFile.xml')


if __name__ == '__main__':

    with open('config.yml','r') as ymlFile:
        config = yaml.load(ymlFile)
    connectionString = 'Server=prime; database=; uid=XXXXXXXXXX;pwd=XXXXXXX;Connect Timeout=1;Pooling=True'
    dbname = 'CanadianCensusTest'
    server = 'DS002\SQLEXPRESS'
    projectName = 'Canadian Census 2011'
    projectYear = '2011'
    metadataFileName = 'CANCEN_2011' # e.g. LEIP1916_PRES
    geoLevelInfoFilePath = 'Z:/Canadian Census/postprocessing/test_external_data_source/edo/geo_level_information.csv'
    tablePrefixName = 'Cancen_'

    configSettings = config(connectionString, dbname, server, projectName, projectYear, metadataFileName, geoLevelInfoFilePath, tablePrefixName) # TODO use in case YAML serialization

    main(connectionString, server,dbname, projectName, projectYear, metadataFileName, geoLevelInfoFilePath, tablePrefixName )