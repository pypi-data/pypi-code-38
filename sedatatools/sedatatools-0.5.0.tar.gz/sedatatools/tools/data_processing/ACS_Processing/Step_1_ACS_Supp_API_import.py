import requests
import pandas as pd
import sys
import time
years = sys.argv[-1]



def getData():

###################Get geo data:

    all_geos = requests.get('http://api.census.gov/data/'+years+'/acsse/geography.json')
    if all_geos.status_code == 200:
        all_data_new = all_geos.json()

    row = []

    for i in all_data_new['fips']:
                row.append([i['name'], i['geoLevelId']])

    geo_desc_df = pd.DataFrame(row, columns=["name", "geoLevelId"])

    geo_desc_df['name'] = geo_desc_df['name'].str.replace(' ', '+')


    geo_desc_df1 = geo_desc_df[['name']]
    geo_desc_df2 = geo_desc_df1['name'].tolist()
    removeset = set([5, 10, 11, 15])
    geo_desc_df3 = [v for i, v in enumerate(geo_desc_df2) if i not in removeset]


###################Get variables data:

    var = pd.read_html('http://api.census.gov/data/'+years+'/acsse/variables.html', header = 0)[0]

    var_subset = var[var['Name'].str.contains("K20")]

    var_desc_df2 = var_subset['Name'].tolist()

    list1 = [','.join(var_desc_df2[x:x+45]) for x in range(0, len(var_desc_df2), 45)]


    pause_after_n_geos_s = 5
    pause_after_n_geos = 10

    pause_after_cty_num_geos_calling_s = 60
    pause_after_cty_num_geos_calling = 700

    pause_after_cty_num_geos_calling_s_all_except_subdiv = 30

    pause_when_error_500_s = 61

###################Get main data:

    appended_data = []
    counter = 0
    geo_counter = 0
    start_time = time.time()
    for index1, el in enumerate(list1):
        for index, geo in enumerate(geo_desc_df3):
            counter = counter + 1
            geo_counter = geo_counter + 1
            if geo_counter == pause_after_cty_num_geos_calling:
                time.sleep(pause_after_cty_num_geos_calling_s_all_except_subdiv)
                geo_counter = 0
            all_data = requests.get(
                'http://api.census.gov/data/' + years + '/acsse?get=' + el + ',NAME,SUMLEVEL&for=' + geo + ':*&key=2938ba69f0d69ef817ee860dc320aa80de939151')
            if counter == pause_after_n_geos:
                time.sleep(pause_after_n_geos_s)
                counter = 0
            if all_data.status_code == 200:  # This means success.
                all_data_new = all_data.json()
                df = pd.DataFrame(all_data_new[1:], columns=all_data_new[0])
                if geo == 'county':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['county'] = df['county'].astype(str).str.zfill(3)
                    df['Geo'] = df[['state', 'county']].apply(lambda x: ''.join(x), axis=1)
                    df.drop(['state', 'county'], axis=1, inplace=True)
                elif geo == 'place':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['place'] = df['place'].astype(str).str.zfill(5)
                    df['Geo'] = df[['state', 'place']].apply(lambda x: ''.join(x), axis=1)
                    df.drop(['state', 'place'], axis=1, inplace=True)
                elif geo == 'alaska+native+regional+corporation':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['alaska native regional corporation'] = df['alaska native regional corporation'].astype(str).str.zfill(5)
                    df['Geo'] = df[['state', 'alaska native regional corporation']].apply(lambda x: ''.join(x),
                                                                                          axis=1)
                    df.drop(['state', 'alaska native regional corporation'], axis=1, inplace=True)
                elif geo == 'necta+division':
                    df['new england city and town area'] = df['new england city and town area'].astype(str).str.zfill(5)
                    df['necta division'] = df['necta division'].astype(str).str.zfill(5)
                    df['Geo'] = df[['new england city and town area', 'necta division']].apply(lambda x: ''.join(x),
                                                                                               axis=1)
                    df.drop(['new england city and town area', 'necta division'], axis=1, inplace=True)
                elif geo == 'congressional+district':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['congressional district'] = df['congressional district'].astype(str).str.zfill(2)
                    df['Geo'] = df[['state', 'congressional district']].apply(lambda x: ''.join(x), axis=1)
                    df.drop(['state', 'congressional district'], axis=1, inplace=True)
                elif geo == 'public+use+microdata+area':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['public use microdata area'] = df['public use microdata area'].astype(str).str.zfill(5)
                    df['Geo'] = df[['state', 'public use microdata area']].apply(lambda x: ''.join(x), axis=1)
                    df.drop(['state', 'public use microdata area'], axis=1, inplace=True)
                elif geo == 'school+district+(elementary)':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['school district (elementary)'] = df['school district (elementary)'].astype(str).str.zfill(5)
                    df['Geo'] = df[['state', 'school district (elementary)']].apply(lambda x: ''.join(x), axis=1)
                    df.drop(['state', 'school district (elementary)'], axis=1, inplace=True)
                elif geo == 'school+district+(secondary)':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['school district (secondary)'] = df['school district (secondary)'].astype(str).str.zfill(5)
                    df['Geo'] = df[['state', 'school district (secondary)']].apply(lambda x: ''.join(x), axis=1)
                    df.drop(['state', 'school district (secondary)'], axis=1, inplace=True)
                elif geo == 'school+district+(unified)':
                    df['state'] = df['state'].astype(str).str.zfill(2)
                    df['school district (unified)'] = df['school district (unified)'].astype(str).str.zfill(5)
                    df['Geo'] = df[['state', 'school district (unified)']].apply(lambda x: ''.join(x), axis=1)
                    df.drop(['state', 'school district (unified)'], axis=1, inplace=True)
                else:
                    df = df.rename(columns={'us': 'Geo'})
                    df = df.rename(columns={'region': 'Geo'})
                    df = df.rename(columns={'division': 'Geo'})
                    df = df.rename(columns={'state': 'Geo'})
                    df = df.rename(columns={'american indian area/alaska native area/hawaiian home land': 'Geo'})
                    df = df.rename(columns={'metropolitan statistical area/micropolitan statistical area': 'Geo'})
                    df = df.rename(columns={'combined statistical area': 'Geo'})
                    df = df.rename(columns={'combined new england city and town area': 'Geo'})
                    df = df.rename(columns={'new england city and town area': 'Geo'})
                    df = df.rename(columns={'urban area': 'Geo'})

                appended_data.append(df)

            else:
                print('Error: ' + all_data.raise_for_status() + ' for variables ' + el + ' for geo ' + geo)
                print(time.time() - start_time)

        result = pd.concat(appended_data)
        result = result.reset_index(drop=True)

        result.to_csv(
            'Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\OutputAPI_data\\' + str(index1) + '_all_other_results.csv',
            index=False, mode='a')

        appended_data = []


# # ################# import principal city--> state-->msa


    appended_data1 = []

    princ_city_code = pd.read_table('Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\Original_Intented_geo\\principal_cities_under_state_under_msa.txt', delimiter='\t',
                                    index_col=False, header=0)

    princ_city_code['FIPS'] = princ_city_code['FIPS'].astype(str).str.zfill(7)

    counter1 = 0
    geo_counter1 = 0
    start_time1 = time.time()
    for index1, el in enumerate(list1):

        for index, row in princ_city_code.iterrows():
            print('File index {} element {} geo index {} geo row {}'.format(str(index1), el, str(index), row))
            counter1 = counter1 + 1
            geo_counter1 = geo_counter1 + 1
            if geo_counter1 == pause_after_cty_num_geos_calling:
                time.sleep(pause_after_cty_num_geos_calling_s_all_except_subdiv)
                geo_counter1 = 0
            all_princ_data = requests.get(
                'http://api.census.gov/data/' + years + '/acsse?get=' + el + ',NAME,SUMLEVEL&for=principal+city:*&in=metropolitan+statistical+area/micropolitan+statistical+area:' + str(
                    row['FIPS'])[-5:] + '+state:' + str(row['FIPS'])[
                                                   :2] + '&key=2938ba69f0d69ef817ee860dc320aa80de939151')
            if counter1 == pause_after_n_geos:
                time.sleep(pause_after_n_geos_s)
                counter1 = 0
            if all_princ_data.status_code == 204:
                continue
            elif all_princ_data.status_code == 200:
                all_princ_data_new = all_princ_data.json()
                df1 = pd.DataFrame(all_princ_data_new[1:], columns=all_princ_data_new[0])
                df1['state'] = df1['state'].astype(str).str.zfill(2)
                df1['metropolitan statistical area/micropolitan statistical area'] = df1['metropolitan statistical area/micropolitan statistical area'].astype(str).str.zfill(5)
                df1['principal city'] = df1['principal city'].astype(str).str.zfill(7)
                df1['Geo'] = df1[['metropolitan statistical area/micropolitan statistical area', 'principal city']].apply(lambda x: ''.join(x), axis=1)
                # df1['Geo'] = df1[['metropolitan statistical area/micropolitan statistical area', 'state',
                #                   'principal city']].apply(lambda x: ''.join(x), axis=1)
                df1.drop(['metropolitan statistical area/micropolitan statistical area', 'state', 'principal city'],
                         axis=1, inplace=True)

                appended_data1.append(df1)

            else:
                print('Error: ' + all_princ_data.raise_for_status() + ' for variables ' + el + ' for geo ' + str(row['FIPS'])[-5:] + str(row['FIPS'])[:2])
                print(time.time() - start_time1)

        all_princ_data_result = pd.concat(appended_data1)
        all_princ_data_result = all_princ_data_result.reset_index(drop=True)
        all_princ_data_result.to_csv(
            'Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\OutputAPI_data\\' + str(index1) + '_principal_cities_under_state_under_msa.csv',
            index=False, mode='a')
        appended_data1 = []

# ################# import county subdivision:

    appended_data2 = []

    county_fips = pd.read_table('Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\Original_Intented_geo\\county_subdivisions.txt', delimiter='\t',
                                    index_col=False, header=0, encoding='utf-16')

    #print(county_fips.columns.values)
    county_fips['FIPS'] = county_fips['FIPS'].astype(str).str.zfill(5)

    counter2 = 0
    geo_counter2 = 0
    start_time2 = time.time()
    for index1, el in enumerate(list1):
        for index, row in county_fips.iterrows():
            print('File index {} element {} geo index {} geo row {}'.format(str(index1), el, str(index), row))
            counter2 = counter2 + 1
            geo_counter2 = geo_counter2 + 1
            if geo_counter2 == pause_after_cty_num_geos_calling:
                time.sleep(pause_after_cty_num_geos_calling_s)
                geo_counter2 = 0

            all_cty_subdiv_data = requests.get(
                'http://api.census.gov/data/' + years + '/acsse?get=' + el + ',NAME,SUMLEVEL&for=county+subdivision:*&in=state:' + str(
                    row['FIPS'])[:2] + '+county:' + str(row['FIPS'])[
                                                    -3:] + '&key=2938ba69f0d69ef817ee860dc320aa80de939151')
            if counter2 == pause_after_n_geos:
                time.sleep(pause_after_n_geos_s)
                counter2 = 0
            if all_cty_subdiv_data.status_code == 204: # NO content
                continue
            elif all_cty_subdiv_data.status_code == 200:
                try:
                    all_cty_subdiv_data_new = all_cty_subdiv_data.json()
                    df2 = pd.DataFrame(all_cty_subdiv_data_new[1:], columns=all_cty_subdiv_data_new[0])
                    df2['state'] = df2['state'].astype(str).str.zfill(2)
                    df2['county'] = df2['county'].astype(str).str.zfill(3)
                    df2['county subdivision'] = df2['county subdivision'].astype(str).str.zfill(5)
                    df2['Geo'] = df2[
                        ['state', 'county', 'county subdivision']].apply(
                        lambda x: ''.join(x), axis=1)
                    df2.drop(['county subdivision', 'state', 'county'], axis=1,
                             inplace=True)

                    appended_data2.append(df2)
                except ValueError:
                    print("Oops! Error Occured: " + ValueError)
            elif all_cty_subdiv_data.status_code == 500: #Internal Server Error
                for i in range(3):
                    print('Code 500 trying' + str(i) + ' of 3')
                    all_cty_subdiv_data = requests.get(
                        'http://api.census.gov/data/' + years + '/acsse?get=' + el + ',NAME,SUMLEVEL&for=county+subdivision:*&in=state:' + str(
                            row['FIPS'])[:2] + '+county:' + str(row['FIPS'])[-3:] + '&key=2938ba69f0d69ef817ee860dc320aa80de939151')
                    if all_cty_subdiv_data.status_code == 200:
                        continue
                    time.sleep(pause_when_error_500_s)
                print(str(row['FIPS']) + ' cannot be downloaded.')
            else:
                print('Error: ' + str(all_cty_subdiv_data.status_code) + ' for variables ' + el + ' for geo ' + str(row['FIPS'])[:2] + str(row['FIPS'])[-3:])
                print(time.time() - start_time2)

        all_cty_subdiv_data_result = pd.concat(appended_data2)
        all_cty_subdiv_data_result = all_cty_subdiv_data_result.reset_index(drop=True)
        all_cty_subdiv_data_result.to_csv(
            'Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\OutputAPI_data\\' + str(index1) + '_county_subdivisions.csv',
            index=False, mode='a')
        appended_data2 = []


################# import NECTA:

    appended_data3 = []

    princity_necta_code = pd.read_table('Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\Original_Intented_geo\\principal_cities_under_NECTA.txt', delimiter='\t',
                                        index_col=False, header=0)

    princity_necta_code['FIPS'] = princity_necta_code['FIPS'].astype(str).str.zfill(7)

    counter3 = 0
    geo_counter3 = 0
    start_time3 = time.time()
    for index1, el in enumerate(list1):
        for index, row in princity_necta_code.iterrows():
            print('File index {} element {} geo index {} geo row {}'.format(str(index1), el, str(index), row))
            counter3 = counter3 + 1
            geo_counter3 = geo_counter3 + 1
            if geo_counter3 == pause_after_cty_num_geos_calling:
                time.sleep(pause_after_cty_num_geos_calling_s_all_except_subdiv)
                geo_counter3 = 0
            princity_necta_data = requests.get(
                'http://api.census.gov/data/' + years + '/acsse?get=' + el + ',NAME,SUMLEVEL&for=principal+city:*&in=new+england+city+and+town+area:' + str(
                    row['FIPS'])[-5:] + '+state:' + str(row['FIPS'])[
                                                    :2] + '&key=2938ba69f0d69ef817ee860dc320aa80de939151')
            if counter3 == pause_after_n_geos:
                time.sleep(pause_after_n_geos_s)
                counter3 = 0
            if princity_necta_data.status_code == 204:
                continue
            elif princity_necta_data.status_code == 200:
                princity_necta_data_new = princity_necta_data.json()
                df3 = pd.DataFrame(princity_necta_data_new[1:], columns=princity_necta_data_new[0])
                df3['new england city and town area'] = df3['new england city and town area'].astype(str).str.zfill(5)
                df3['principal city'] = df3['principal city'].astype(str).str.zfill(5)
                df3['Geo'] = df3[
                    ['new england city and town area', 'principal city']].apply(
                    lambda x: ''.join(x), axis=1)
                df3.drop(['principal city', 'state', 'new england city and town area'], axis=1,
                         inplace=True)

                appended_data3.append(df3)
            else:
                print('Error: ' + str(princity_necta_data.status_code) + ' for variables ' + el + ' for geo ' + str(row['FIPS']))
                print(time.time() - start_time3)

        princity_necta_data = pd.concat(appended_data3)
        princity_necta_data = princity_necta_data.reset_index(drop=True)
        princity_necta_data.to_csv(
            'Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\OutputAPI_data\\' + str(index1) + '_principal_cities_under_NECTA.csv',
            index=False, mode='a')
        appended_data3 = []

# ################# import metro divison under MSA:

    appended_data4 = []

    metro_div_code = pd.read_table('Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\Original_Intented_geo\\metro_division_under_msa.txt', delimiter='\t',
                                   index_col=False, header=0)

    metro_div_code['FIPS'] = metro_div_code['FIPS'].astype(str).str.zfill(5)

    counter4 = 0
    geo_counter4 = 0
    start_time4 = time.time()

    for index1, el in enumerate(list1):
        for index, row in metro_div_code.iterrows():
            print('File index {} element {} geo index {} geo row {}'.format(str(index1), el, str(index), row))
            counter4 = counter4 + 1
            geo_counter4 = geo_counter4 + 1
            if geo_counter4 == pause_after_cty_num_geos_calling:
                time.sleep(pause_after_cty_num_geos_calling_s_all_except_subdiv)
                geo_counter4 = 0
            metro_div_data = requests.get(
                'http://api.census.gov/data/' + years + '/acsse?get=' + el + ',NAME,SUMLEVEL&for=metropolitan+division:*&in=metropolitan+statistical+area:' + str(
                    row['FIPS']) + '&key=2938ba69f0d69ef817ee860dc320aa80de939151')
            if counter4 == pause_after_n_geos:
                time.sleep(pause_after_n_geos_s)
                counter4 = 0
            if metro_div_data.status_code == 204:
                continue
            elif metro_div_data.status_code == 200:
                metro_div_data_new = metro_div_data.json()
                df4 = pd.DataFrame(metro_div_data_new[1:], columns=metro_div_data_new[0])
                df4['metropolitan statistical area'] = df4['metropolitan statistical area'].astype(str).str.zfill(5)
                df4['metropolitan division'] = df4['metropolitan division'].astype(str).str.zfill(5)
                df4['Geo'] = df4[
                    ['metropolitan statistical area', 'metropolitan division']].apply(
                    lambda x: ''.join(x), axis=1)
                df4.drop(['metropolitan statistical area', 'metropolitan division'], axis=1,
                         inplace=True)

                appended_data4.append(df4)

            else:
                print('Error: ' + str(metro_div_data.status_code) + ' for variables ' + el + ' for geo ' + str(row['FIPS']))
                print(time.time() - start_time4)

        metro_div_data_result = pd.concat(appended_data4)
        metro_div_data_result = metro_div_data_result.reset_index(drop=True)
        metro_div_data_result.to_csv(
            'Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\OutputAPI_data\\' + str(index1) + '_metro_division_under_msa.csv',
            index=False, mode='a')
        appended_data4 = []


def processFiles():
    getData()

if __name__ == '__main__':
    processFiles()

