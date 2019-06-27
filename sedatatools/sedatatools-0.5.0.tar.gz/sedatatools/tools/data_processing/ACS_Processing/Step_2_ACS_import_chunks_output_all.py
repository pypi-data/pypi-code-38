import pandas as pd
import os, sys
years = sys.argv[-1]


def get_data():

    path = r'Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\OutputAPI_data\\'  # use your path
    dirs = os.listdir(path)

    all_files1 = []
    for file1 in dirs:
        if '_all_other_results' in file1:
            files1 = path+file1
            all_files1.append(files1)

    all_files2 = []
    for file2 in dirs:
        if '_county_subdivisions' in file2:
            files2 = path + file2
            all_files2.append(files2)

    all_files3 = []
    for file3 in dirs:
        if '_metro_division_under_msa' in file3:
            files3 = path + file3
            all_files3.append(files3)

    all_files4 = []
    for file4 in dirs:
        if '_principal_cities_under_NECTA' in file4:
            files4 = path + file4
            all_files4.append(files4)

    all_files5 = []
    for file5 in dirs:
        if '_principal_cities_under_state_under_msa' in file5:
            files5 = path + file5
            all_files5.append(files5)

#get geos so you can merge it, and also you can use it for geo file

    frame1 = pd.DataFrame()
    list_1 = []
    for file_1 in all_files1:
        df1 = pd.read_csv(file_1, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str}, usecols=['Geo','SUMLEVEL', 'NAME'])
        df1 = df1.drop_duplicates()
        list_1.append(df1)

    frame1 = pd.concat(list_1)

    for file_ in all_files1:
        df = pd.read_csv(file_, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str})
        frame1 = pd.merge(frame1, df, how='left', on=['Geo', 'SUMLEVEL', 'NAME'])
        frame1 = frame1.drop_duplicates(['Geo', 'SUMLEVEL', 'NAME'], keep='last')

    frame2 = pd.DataFrame()
    list_2 = []
    for file_2 in all_files2:
        df2 = pd.read_csv(file_2, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str}, usecols=['Geo', 'SUMLEVEL', 'NAME'])
        df2 = df2.drop_duplicates()
        list_2.append(df2)

    frame2 = pd.concat(list_2)

    for file_ in all_files2:
        df = pd.read_csv(file_, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str})
        frame2 = pd.merge(frame2, df, how='left', on=['Geo', 'SUMLEVEL', 'NAME'])
        frame2 = frame2.drop_duplicates(['Geo', 'SUMLEVEL', 'NAME'], keep='last')
        cols = [c for c in frame2.columns if c.lower()[-2:] != '_x']

        frame2 = frame2[cols]
        frame2.columns = frame2.columns.str.replace('_y', '')
        list_1.append(frame2)

    frame3 = pd.DataFrame()
    list_3 = []
    for file_3 in all_files3:
        df3 = pd.read_csv(file_3, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str}, usecols=['Geo', 'SUMLEVEL', 'NAME'])
        df3 = df3.drop_duplicates()
        list_3.append(df3)

    frame3 = pd.concat(list_3)

    for file_ in all_files3:
        df = pd.read_csv(file_, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str})
        frame3 = pd.merge(frame3, df, how='left', on=['Geo', 'SUMLEVEL', 'NAME'])
        frame3 = frame3.drop_duplicates(['Geo', 'SUMLEVEL', 'NAME'], keep='last')

    frame4 = pd.DataFrame()
    list_4 = []
    for file_4 in all_files4:
        df4 = pd.read_csv(file_4, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str}, usecols=['Geo', 'SUMLEVEL', 'NAME'])
        df4 = df4.drop_duplicates()
        list_4.append(df4)

    frame4 = pd.concat(list_4)

    for file_ in all_files4:
        df = pd.read_csv(file_, index_col=None, header=0, converters={'Geo': str}, encoding='ISO-8859-1')
        frame4 = pd.merge(frame4, df, how='left', on=['Geo', 'SUMLEVEL', 'NAME'])
        frame4 = frame4.drop_duplicates(['Geo', 'SUMLEVEL', 'NAME'], keep='last')

    frame5 = pd.DataFrame()
    list_5 = []
    for file_5 in all_files5:
        df5 = pd.read_csv(file_5, index_col=None, header=0, encoding='ISO-8859-1', converters={'Geo': str}, usecols=['Geo', 'SUMLEVEL', 'NAME'])
        df5 = df5.drop_duplicates()
        list_5.append(df5)

    frame5 = pd.concat(list_5)

    for file_ in all_files5:
        df = pd.read_csv(file_, index_col=None, header=0, converters={'Geo': str}, encoding='ISO-8859-1')
        frame5 = pd.merge(frame5, df, how='left', on=['Geo', 'SUMLEVEL', 'NAME'])
        frame5 = frame5.drop_duplicates(['Geo', 'SUMLEVEL', 'NAME'], keep='last')

    frames_all = [frame1, frame2, frame3, frame4, frame5]

    result = pd.concat(frames_all, ignore_index=True)

    result.to_csv('Z:/ACS_Supplemental/Raw Data/'+years+'/OutputAPI_data/ACS_Supplemental_raw_data.csv', converters={'Geo': str}, index=False)

def processFiles():
    get_data()

if __name__ == '__main__':
    processFiles()

