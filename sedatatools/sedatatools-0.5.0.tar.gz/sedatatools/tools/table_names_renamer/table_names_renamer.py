import csv
from lxml import etree as ET


def get_metadata_file(file_loc):
    parser = ET.XMLParser(strip_cdata=False)
    doc = ET.parse(file_loc, parser)
    return doc

def get_names_file(names_file_loc):
    new_old_cdb = {}
    with open(names_file_loc, 'r') as rf:
        rdr = csv.reader(rf)
        for row in rdr:
            new_old_cdb[row[0]] = row[1]

    return new_old_cdb

def rename_metadata_file(metadata_file, names_file):
    for elem in metadata_file.xpath('//tables/table'):
        try:
            if len(elem.xpath('OutputFormat')[0].attrib['TableTitle']) > 0:
                elem.xpath('OutputFormat')[0].attrib['TableTitle'] = names_file[
                    elem.xpath('OutputFormat')[0].attrib['TableTitle']]
            elem.attrib['title'] = names_file[elem.attrib['title']]
            elem.attrib['titleWrapped'] = names_file[elem.attrib['titleWrapped']]
        except KeyError:
            continue
    return metadata_file

def write_file(metadata_file_fixed):
    # ET.tostring(metadata_file_fixed, pretty_print=True)
    metadata_file_fixed.write('../processing data/out/LEHD2014_ren.xml')


if __name__ == '__main__':
    # 1. import metadata file to rename tables
    metadata_file = get_metadata_file('../processing data/out/LEHD2014.xml')
    # 2. import csv with new names in format "old name","new name"
    names_file = get_names_file('../processing data/out/preparation files for review version/old_vs_new_table_names.csv')
    # 3. rename tables
    metadata_file_fixed = rename_metadata_file(metadata_file, names_file)
    # 4. write to file
    write_file(metadata_file_fixed)
