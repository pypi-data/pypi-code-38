from lxml import etree as et
import os
import pandas as pd
if __name__ == '__main__':
    meta_dir = 'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata'
    files_list = os.listdir(meta_dir)
    files_list = [f for f in files_list if '.xml' in f]
    vars_to_check = []
    for file in files_list:
        # if file == 'C1850 Metadata.xml':
        doc = et.parse(os.path.join(meta_dir,file))
        tables_to_check = doc.xpath('//table[@DollarYear="0"]')
        for table in tables_to_check:
            variables = table.xpath('.//variable[@formatting="7"]/@name')
            if len(variables) > 0:
                vars_to_check.append([file, table.attrib['name'], variables])
    print(*vars_to_check)
    pd.DataFrame(data=vars_to_check).to_csv('lst.csv', index=False)
