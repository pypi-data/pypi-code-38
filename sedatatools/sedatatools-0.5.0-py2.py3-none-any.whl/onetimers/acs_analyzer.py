from lxml import etree as et
import os
import pandas as pd

def get_list_files(fl_dir):
    files = os.listdir(fl_dir)
    files = [f for f in files if 'ACS' in f
             and 'CVAP' not in f
             and 'stimate' not in f
             and 'COMP' not in f
             and 'Comp' not in f
             and 'Docs' not in f
             and 'Image' not in f
             and 'White' not in f
             and 'batch' not in f
             and 'Fitz' not in f
             ]
    return files


def get_tables(file_path):
    doc = et.parse(file_path)
    ds = doc.xpath('//SurveyDataset[@abbreviation="SE"]')
    try:
        tables = ds[0].xpath('.//table')
    except IndexError:
        print(f'DS abbreviation is not ok for {file_path} {[i.attrib["abbreviation"].join(", ") for i in ds]}')
        return {}
    return {t.attrib['name']: t.attrib['title'] for t in tables}


def check_match(check_projs):
    baseline_project = 'ACS 2016-5yr Metadata.xml'
    writer = pd.ExcelWriter('acs_analyzer_results.xlsx', engine='xlsxwriter')
    stats_data = []
    for project_name, v in check_projs.items():
        if project_name == baseline_project:
            continue
        else:
            print(f'Comparing {baseline_project} vs. {project_name}')
            matching = 0
            missing = 0
            non_matching = 0
            missing_vars = []
            matching_vars = []
            non_matching_vars = []
            number_of_vars = len(check_projs[baseline_project])

            for name, title in v.items():
                if name in list(check_projs[baseline_project].keys()):
                    if title == check_projs[baseline_project][name]:
                        matching += 1
                        matching_vars.append([name, title])
                    else:
                        non_matching += 1
                        non_matching_vars.append([name, title])
                else:
                    missing += 1
                    missing_vars.append([name, title])
            print(f'Done! Missing {missing} ({round(missing/number_of_vars*100,2)}), '
                  f'matching: {matching} ({round(matching/number_of_vars*100,2)}), '
                  f'non matching {non_matching} ({round(non_matching/number_of_vars*100,2)})')

            stats_data.append([project_name, str(matching)+' ('+str(round(matching/number_of_vars*100, 2))+'%)',
                               str(missing)+' ('+str(round(missing/number_of_vars*100, 2))+'%)',
                               str(non_matching)+' ('+str(round(non_matching/number_of_vars*100, 2))+'%)'])
            max_v = max(missing, matching, non_matching)
            df = pd.DataFrame({'Missing': missing_vars + ['']*(max_v - len(missing_vars)),
                               'Matching': matching_vars+ ['']*(max_v - len(matching_vars)),
                               'Non matching': non_matching_vars + ['']*(max_v - len(non_matching_vars))
                               })

            df.to_excel(writer, project_name, index=False)
    df_stats = pd.DataFrame(data=stats_data, columns=['Project name', 'Matching', 'Missing', 'Non matching'])
    df_stats.to_excel(writer, 'STATS', index=False)
    writer.save()


if __name__ == '__main__':
    path_to_files = 'C:\Projects\Website-ASP.NET\pub\ReportData\Metadata'
    # get list of files
    files = get_list_files(path_to_files)
    # get list of tables
    proj_tabs = {}
    for file in files:
        proj_tabs[file] = get_tables(os.path.join(path_to_files, file))
    # calculate differences and get list of different vars
    check_match(proj_tabs)