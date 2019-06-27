# import classes
# import pandas as pd
import time
from lxml import etree as et
import os
import pickle


def name_type(dtype):
    if dtype == '3':
        return 'integer'
    else:
        return 'unknown'


class Survey:
    # publisher, year categories
    def __init__(self, name, display_name, guid, visibility, optimized_retrieval, datasets):
        self.name = name
        self.display_name = display_name
        self.guid = guid
        self.visibility = visibility
        self.optimized_retrieval = optimized_retrieval
        self.datasets = datasets

    name = ''
    display_name = ''
    guid = ''
    visibility = False
    optimized_retrieval = ''
    datasets = {}


class Dataset:
    def __init__(self, name, guid, abbreviation, display_name, visibility, tables):
        self.name = name
        self.guid = guid
        self.abbreviation = abbreviation
        self.display_name = display_name
        self.visibility = visibility
        self.tables = tables

    name = ''
    guid = ''
    abbreviation = ''
    publisher = ''
    visibility = False
    tables = {}


class Table:
    def __init__(self, name, title, guid, visibility_report, visibility_map, variables):
        self.name = name
        self.title = title
        self.guid = guid
        self.visibility_report = visibility_report
        self.visibility_map = visibility_map
        self.variables = variables

    def values(self):
        pass
    name = ''
    title = ''
    guid = ''
    visibility_map = False
    visibility_report = False
    variables = {}


class Variables:
    def __init__(self, name, label, qlabel, guid, formula, db_type):
        self.name = name
        self.label = label
        self.qlabel = qlabel
        self.guid = guid
        self.formula = formula
        self.db_type = db_type

    def values(self):
        pass

    name = ''
    label = ''
    qlabel = ''
    guid = ''
    formula = ''
    db_type = ''
    db_type_exp = name_type(db_type)


def get_files_list(path_to_file):
    files = os.listdir(path_to_file)
    xmls = [filename for filename in files if '.xml' in filename]
    return xmls


def process_xml(xml_doc_location):
    survey_data = {}
    doc = et.parse(xml_doc_location)
    try:
        survey = doc.xpath('/survey')[0]
    except IndexError:
        print(f'Survey without name ?! {xml_doc_location}')
        return {'': ''}
    survey_name = survey.attrib['name']
    survey_display_name = survey.attrib['DisplayName']
    try:
        survey_guid = survey.attrib['GUID']
    except KeyError:
        print('stop')
    survey_vis = survey.attrib['Visible']
    try:
        # some old xmls don't have this tag
        survey_optimized_retrieval = survey.xpath('//UseOptimizedDataRetrieval')[0].text
    except IndexError:
        survey_optimized_retrieval = []

    dataset_data = {}
    datasets = doc.xpath('//SurveyDataset')
    for dataset in datasets:
        try:
            dataset_name = dataset.attrib['name']
            dataset_abbreviation = dataset.attrib['abbreviation']
            dataset_display_name = dataset.attrib['DisplayName']
            dataset_guid = dataset.attrib['GUID']
            dataset_vis = dataset.attrib['Visible']
        except KeyError:
            dataset_name = ''
            dataset_display_name = ''
            dataset_guid = ''
            dataset_vis = False

        table_data = {}
        tables = dataset.xpath('./tables/table')
        for table in tables:
            # universe, titlewraped
            table_name = table.attrib['name']
            table_title = table.attrib['title']
            table_guid = table.attrib['GUID']
            table_visible_tab = table.attrib['Visible']
            try:
                table_visible_map = table.attrib['VisibleInMaps']
            except KeyError:
                # some older projects are missing this attribute probably
                table_visible_map = True

            variable_data = {}
            variables = table.xpath('./variable')
            for variable in variables:
                # variable type
                variable_name = variable.attrib['name']
                variable_label = variable.attrib['label']
                variable_qlabel = variable.attrib['qLabel']
                variable_guid = variable.attrib['GUID']
                variable_formula = variable.attrib['FormulaFunctionBodyCSharp']
                variable_data_type = variable.attrib['dataType']
                variable_data[variable_name] = Variables(name=variable_name,
                                                         label=variable_label,
                                                         qlabel=variable_qlabel,
                                                         guid=variable_guid,
                                                         formula=variable_formula,
                                                         db_type=variable_data_type)
            table_data[table_name] = Table(name=table_name,
                                           title=table_title,
                                           guid=table_guid,
                                           visibility_report=table_visible_tab,
                                           visibility_map=table_visible_map,
                                           variables=variable_data)
        dataset_data[dataset_abbreviation] = Dataset(name=dataset_name,
                                                     display_name=dataset_display_name,
                                                     guid=dataset_guid,
                                                     abbreviation=dataset_abbreviation,
                                                     visibility=dataset_vis,
                                                     tables=table_data)
    survey_data[survey_name] = Survey(name=survey_name,
                                      display_name=survey_display_name,
                                      guid=survey_guid,
                                      visibility=survey_vis,
                                      optimized_retrieval=survey_optimized_retrieval,
                                      datasets=dataset_data)
    return survey_data


def meta_details(create_cache, path='C:/Projects/Website-ASP.NET/pub/ReportData/Metadata'):
    projects_details = {}
    if os.path.exists('projects_details.pkl') and not create_cache:
        projects_details = pickle.load(open('projects_details.pkl', 'rb'))
    else:
        print('Just a sec, collecting metadata info: ')
        for xml_doc in get_files_list(path):
            print(xml_doc)
            projects_details = {**projects_details, **process_xml(os.path.join(path, xml_doc))}
        pickle.dump(projects_details, open('projects_details.pkl', 'wb'))
    return projects_details

if __name__ == '__main__':
    start_time = time.time()
    path_to_dir = 'C:/Projects/Website-ASP.NET/pub/ReportData/Metadata'
    cache = False
    projects = meta_details(cache, path_to_dir)
    print(f'Done in {time.time() - start_time}')
# process_xml('C:/Projects/Website-ASP.NET/pub/ReportData/Metadata/ACS 2013-5yr Metadata.xml')
