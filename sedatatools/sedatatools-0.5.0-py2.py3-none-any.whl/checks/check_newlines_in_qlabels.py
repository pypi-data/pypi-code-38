import lxml
from lxml import etree as et
import os
import progressbar

project_files = [os.path.join('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata', f)
                 for f in os.listdir('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata') if f.endswith('.xml')]


def check_newlines_in_labels(files):
    exclusions = ['C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\Crime_Popest_2010.xml',
                  'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\Crime_Popest_2012.xml',
                  'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\RC1980_COMP.xml',
                  'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\RC1980.xml',
                  'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\C1980 Metadata v1.xml',
                  ]
    fix_errors = False
    errors = []
    for file in progressbar.progressbar(files):
        if file in exclusions:
            continue
        parser = et.XMLParser(strip_cdata=False)
        try:
            doc = et.parse(file, parser=parser)
        except lxml.etree.XMLSyntaxError:
            print(f'File {file} unparsable!')
        variables = doc.xpath('//variable')
        for v in variables:
            if '\r\n' in v.attrib['qLabel']:
                print(f"Error in file {file}, variable {v.attrib['name']}, label {v.attrib['label']}, "
                      f"qlabel {v.attrib['qLabel'] }")
                errors.append([file, v.attrib['name'], v.attrib['label'], v.attrib['qLabel']])
                if fix_errors:
                    print(f"Fixing error in file {file}, variable {v.attrib['name']}")
                    v.attrib['qLabel'] = v.attrib['qLabel'].replace('\r\n', '')
                    doc.write(file, pretty_print=True)
    print(f'{len(errors)} errors found!')
    return errors


check_newlines_in_labels(project_files)
