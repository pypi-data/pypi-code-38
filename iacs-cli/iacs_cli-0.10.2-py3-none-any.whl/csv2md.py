import os, csv, datetime, re

from .find_docs import find_docs

def csv2md(csv_file):
    csv_file = os.path.abspath(csv_file)

    root_dir = os.getcwd()
    document_dir = find_docs(os.path.join(root_dir, 'content/'))

    with open(csv_file, 'r') as file:
        csv_table = csv.reader(file)

        schedule_md = os.path.join(root_dir, 'content/pages/schedule.md')
        with open(schedule_md, 'w') as md_file:
            md_file.write('Title: Schedule\n')
            md_file.write('Slug: schedule\n')
            date = datetime.date.today()
            md_file.write('Date: ' + date.strftime("%Y-%m-%d") + '\n\n\n')

            for i, row in enumerate(csv_table):

                row_mod = list()
                for item in row:
                    idx = re.match("^([^:]*)", item)
                    doc_type = idx.group(0) if idx else None
                    if doc_type in document_dir:
                        url = re.search("/content(.*)", document_dir[doc_type])
                        url = "{filename}"+url.group(1)
                        item = '[' + item + ']'+ '(' + url + ')'
                    row_mod.append(item)

                md_file.write('|' + '|'.join(row_mod) + '|\n')
                if i == 0:
                    header_line = ['-'*5 for j in range(len(row))]
                    md_file.write('|' + '|'.join(header_line) + '|\n')
