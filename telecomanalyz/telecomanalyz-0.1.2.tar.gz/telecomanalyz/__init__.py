import numpy as np
from matplotlib.path import Path
from sqlalchemy import create_engine
import pandas as pd
import folium
from folium.plugins import MeasureControl
import webbrowser
from bs4 import BeautifulSoup
from scipy.spatial import KDTree
from multiprocessing.dummy import Pool as ThreadPool
import geopy.distance
import time
import os
from math import atan, cos, pi, radians
import datetime
import threadpool
import random
from math import sin, asin, cos, radians, fabs, sqrt,pi,cos,atan,tan,acos,degrees,atan2
from geographiclib.geodesic import Geodesic
import mplleaflet
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool
from scipy.spatial import ConvexHull

# 显示所有列
pd.set_option('display.max_rows', None)
# 显示所有行
pd.set_option('display.max_columns', None)
# 不换行
pd.set_option('display.width', None)

def timestamp_to_format(timestamp=None,format = '%Y-%m-%d %H:%M:%S'):
    # try:
    if timestamp:
        time_tuple = time.localtime(timestamp)
        print('time_tuple:',time_tuple)
        #print('type(time_tuple):',type(time_tuple))
        res = time.strftime(format,time_tuple)
    else:
        res = time.strftime(format)
    return res

def randomcolor(rejectcolor):
    for rjtcolor in range(200000000):
        colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        color = ""
        for i in range(6):
            color += colorArr[random.randint(0,14)]
        if "#"+color not in rejectcolor:
            return "#"+color
            break

def get_distance(latloninterval):
    # point格式为[起点lat，起点lon，终点lat，终点lon]
    lat_a = latloninterval[0]
    lon_a = latloninterval[1]
    lat_b = latloninterval[2]
    lon_b = latloninterval[3]

    radlat1 = radians(lat_a)
    radlat2 = radians(lat_b)
    a = radlat1 - radlat2
    b = radians(lon_a) - radians(lon_b)
    s = 2 * asin(sqrt(pow(sin(a/2),2) + cos(radlat1) * cos(radlat2)*pow(sin(b/2),2)))
    earth_radius = 6378137
    s = s * earth_radius
    return s

def get_distance_single(latlonsou,latlontag):
    # point格式为[起点lat，起点lon，终点lat，终点lon]
    lat_a = latlonsou[0]
    lon_a = latlonsou[1]
    lat_b = latlontag[0]
    lon_b = latlontag[1]

    radlat1 = radians(lat_a)
    radlat2 = radians(lat_b)
    a = radlat1 - radlat2
    b = radians(lon_a) - radians(lon_b)
    s = 2 * asin(sqrt(pow(sin(a/2),2) + cos(radlat1) * cos(radlat2)*pow(sin(b/2),2)))
    earth_radius = 6378137
    s = s * earth_radius
    return s

def changwebpage(webfilename, sou, tag):
    file = webfilename
    content = open(file, 'r', encoding="utf-8")
    html_cont = content.read()
    find_content = BeautifulSoup(html_cont, 'lxml')

    for change_script in find_content.find_all('script', src=True):
        print(change_script, change_script['src'])
        change_script.get_text(strip=True)
        if change_script['src'] == sou:
            change_script['src'] = tag
    change_content = str(find_content).encode(encoding='utf-8')  # 尤其注意，soup生成了字典，进行修改后要转为str，并将其固定utf-8编码，才能存回去
    change_html = open(file, "w+b")
    change_html.write(change_content)
    change_html.close()
    print(file + ' ' + 'changed!')

def InputMRtoSql(path,sqlfilename,changciname,cityname,sqlengine):
    # 各地市MR数据导入sql
    # 除256取商就是enodeBid，CI - enodeBid * 256 = cellid
    filelist = os.listdir(path)
    cityen = ['ANQING', 'BENGBU', 'BOZHOU', 'CHIZHOU', 'CHUZHOU', 'FUYANG', 'HEFEI', 'HUAIBEI', 'HUAINAN', 'HUANGSHAN',
              'LIUAN', 'MAANSHAN', 'SUZHOU', 'TONGLING', 'WUHU', 'XUANCHENG']
    print(cityen[5])
    citych = ['安庆', '蚌埠', '亳州', '池州', '滁州', '阜阳', '合肥', '淮北', '淮南', '黄山', '六安', '马鞍山', '宿州', '铜陵', '芜湖', '宣城']
    citydic = {cityen[i]: citych[i] for i in range(len(cityen))}
    print(path)
    print(filelist)
    for file in filelist:
        print(path + file)
        MRtemp = pd.read_csv(path + file, sep=',', low_memory=False, encoding='gb18030')
        MRtemp[changciname] = MRtemp.栅格主覆盖CI.apply(lambda x: str(x // 256) + str(x - x // 256 * 256))
        MRtemp[cityname] = MRtemp.城市.apply(lambda x: citydic[x])
        MRtemp.columns = ['Ci', 'city','Lon', 'Lat',  'CellMRCount', 'AvgeRSRQ']
        print(MRtemp.head())
        MRtemp.to_sql(sqlfilename, con=sqlengine, if_exists='append', index=False, chunksize=10)


def Get_Angle(latloninterval):
    # point格式为[起点lat，起点lon，终点lat，终点lon]
    angle = 0.0
    dx = (latloninterval[3] - latloninterval[1]) * cos(radians(latloninterval[2]))
    dy = latloninterval[2] - latloninterval[0]
    if latloninterval[3] == latloninterval[1]:
        angle = pi / 2.0
        if latloninterval[2] == latloninterval[0]:
            angle = 0.0
        elif latloninterval[2] < latloninterval[0]:
            angle = 3.0 * pi / 2.0
    elif latloninterval[3] > latloninterval[1] and latloninterval[2] > latloninterval[0]:
        angle = atan(dx / dy)
    elif latloninterval[3] > latloninterval[1] and latloninterval[2] < latloninterval[0]:
        angle = pi / 2 + atan(-dy / dx)
    elif latloninterval[3] < latloninterval[1] and latloninterval[2] < latloninterval[0]:
        angle = pi + atan(dx / dy)
    elif latloninterval[3] < latloninterval[1] and latloninterval[2] > latloninterval[0]:
        angle = 3.0 * pi / 2.0 + atan(dy / -dx)
    return (angle * 180 / pi)


def drawbandmap(bandg,idname,popname,color,fillOpacity,mapname):
    latlonband = np.array(bandg[['Lon', 'Lat']]).tolist()
    bandgeo = {"type": "FeatureCollection",
               "features": [
                   {
                       "properties": {"name": 'band'},
                       "id": idname,
                       "type": "Feature",
                       "geometry": {
                           "type": "Polygon",
                           "coordinates": [latlonband]
                       }
                   }]}


    style_function = lambda feature: {'fillOpacity': fillOpacity,
                                      'weight': 2,
                                      'fillColor': color,
                                      'color': color
                                      }

    gj = folium.GeoJson(bandgeo,style_function=style_function)
    gj.add_child(folium.Popup(popname))
    gj.add_to(mapname)

def Get_Appendband(twoinfo):
    # twoinfo:[twoinfo[0], appenddistance]
    # 输入一组pandas格式的，包含字段'Lat', 'Lon'格式的点，输出凸包及凸包扩展点
    print(twoinfo[0][['Lat', 'Lon']])
    twoinfo[0] = np.array(twoinfo[0][['Lat', 'Lon']])
    hull = ConvexHull(twoinfo[0])
    mask = hull.vertices
    mask = np.append(mask, mask[0])
    RTLheanband = twoinfo[0][mask, :]

    # folium.PolyLine(locations=RTLheanband, color='green').add_to(m)
    RTLheanband=np.vstack([RTLheanband,RTLheanband[1]])
    RTLheanband = pd.DataFrame(RTLheanband, columns=['Lat', 'Lon'])

    resultlatlon = []

    for i in range(1, len(RTLheanband)-1):
        firstdirction = Get_Angle(
            [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], RTLheanband.iloc[i - 1]['Lat'],
             RTLheanband.iloc[i - 1]['Lon']])
        seconddirction = Get_Angle(
            [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], RTLheanband.iloc[i + 1]['Lat'],
             RTLheanband.iloc[i + 1]['Lon']])
        directionD = min([abs(seconddirction - firstdirction),
                          abs(seconddirction - firstdirction - 360),
                          abs(seconddirction - firstdirction + 360)])

        # resultdirecton = firstdirction - (180 - directionD / 2)
        resultlong = twoinfo[1] / sin(radians(directionD / 2))

        # movelatlon = Get_distance_point(
        #     [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], firstdirction, (180 - directionD / 2),
             # resultlong])
        # folium.Circle(location=movelatlon, radius=10, color='red').add_to(m)

        resultlatlon.append(Get_distance_point(
            [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], firstdirction, (180 - directionD / 2),
             resultlong]))
        #
        # print(resultlatlon)
    resultlatlon.append(resultlatlon[0])
    Appendband = pd.DataFrame(resultlatlon, columns=['Lat', 'Lon'])
    return RTLheanband[:-1],Appendband


def Get_parallel_line(linepoint,distance):
    resultlatlon = []
    colbin=linepoint.columns.values.tolist()
    for i in range(0, len(linepoint)):
        try:
            firstdirction = Get_Angle(
                [linepoint.iloc[i]['Lat'], linepoint.iloc[i]['Lon'], linepoint.iloc[i - 1]['Lat'],
                 linepoint.iloc[i - 1]['Lon']])
        except:
            firstdirction=180
        try:
            seconddirction = Get_Angle(
                [linepoint.iloc[i]['Lat'], linepoint.iloc[i]['Lon'], linepoint.iloc[i + 1]['Lat'],
                 linepoint.iloc[i + 1]['Lon']])
        except:
            seconddirction=180

        directionD = min([abs(seconddirction - firstdirction),
                          abs(seconddirction - firstdirction - 360),
                          abs(seconddirction - firstdirction + 360)])

        # resultdirecton = firstdirction - (180 - directionD / 2)
        resultlong = distance/ sin(radians(directionD / 2))

        # movelatlon = Get_distance_point(
        #     [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], firstdirction, (180 - directionD / 2),
             # resultlong])
        # folium.Circle(location=movelatlon, radius=10, color='red').add_to(m)


        temp=linepoint[i:i+1].values.tolist()
        temp=temp[0]+Get_distance_point([linepoint.iloc[i]['Lat'],linepoint.iloc[i]['Lon'], firstdirction, -(180 - directionD / 2),
             resultlong])
        resultlatlon.append(temp)

        #
        # print(resultlatlon)
    parallel_line = pd.DataFrame(resultlatlon, columns=colbin+['Latparallel', 'Lonparallel'])
    parallel_line['Lat']=parallel_line['Latparallel']
    parallel_line['Lon'] = parallel_line['Lonparallel']
    return parallel_line

    
    
def Pointinband(tooinfo):
    # tooinfo为列表结构，包含两个元素point, band,都为pandas数据结构
    # 输出为pandas结构

    pointcolumns=tooinfo[0].columns.values.tolist()

    codes=[Path.MOVETO]
    for bandlong in range(1,len(tooinfo[1])-1):
        codes.append(Path.LINETO)
    codes.append(Path.CLOSEPOLY)

    bandlatlon=tooinfo[1][['Lat','Lon']]

    pointlonlat=tooinfo[0][['Lat','Lon']]
    # [[tooinfo[0].iloc[i]['Lat'], tooinfo[0].iloc[i]['Lon']] for i in range(0, len(tooinfo[0]))]

    pth = Path(bandlatlon, codes)
    mask = pth.contains_points(pointlonlat)


    if len(np.array(tooinfo[0])[mask,:]):
        result=pd.DataFrame(np.array(tooinfo[0])[mask,:],columns=pointcolumns)
        result['bandname']=tooinfo[1].iloc[0]['Name']
        return result
    else:
        print('边框内无点')





def Nearbandcell(point,band):
    colu=point.columns.values.tolist()
    print(colu)
    gruopbandnametemp = list(set(band['Name']))[0]
    Bandcenter=getGcentre(band)


    inbandpoint=Pointinband([point,band])


    try:
        inBandname = list(set(inbandpoint['小区名称']))
        point =point[~point.小区名称.isin(inBandname)]


    except:
        print('非必选包含关系点')

    point = point[point.type == 'outdoor']



    bandresults=[]
    for bandid in range(len(band)):
        colu = point.columns.values.tolist()
        bandpointlatlon = band[bandid:bandid+1][['Lat', 'Lon']].values.tolist()[0]
        print(bandpointlatlon)
        tree = KDTree(point[['Lat', 'Lon']])
        cellout = tree.query(bandpointlatlon, k=15)

        Ltecellmark = cellout[1].flatten()
        # 生成临近点距离、index列表
        print(np.array([bandpointlatlon] * len(Ltecellmark)))
        near = np.vstack(
            (np.array([gruopbandnametemp] * len(Ltecellmark)), np.array([bandpointlatlon] * len(Ltecellmark)).T)).T
        # 转置并去重
        LOONear = point.iloc[Ltecellmark, :]

        # 提取从非边界内小区中提出临近的datafram表

        print(near[0:10])
        LOONear = np.hstack((np.array(LOONear), near))
        print(colu)
        colu=colu+['bandname','bandpointlat','bandpointlon']
        print(colu)
        results=pd.DataFrame(LOONear,columns=colu)
        bandresults.append(results)

    results=pd.concat(bandresults,ignore_index=True)
    results[['Lat', 'Lon', 'bandpointlat', 'bandpointlon']] = results[['Lat', 'Lon', 'bandpointlat', 'bandpointlon']].astype(float)
    results['distance']=[get_distance(results[i:i+1][['Lon', 'Lat']].values.tolist()[0]+results[i:i+1][['bandpointlon', 'bandpointlat']].values.tolist()[0]) for i in
                               range(len(results))]

    results.sort_values(by=["bandname", '小区名称', 'distance'], ascending=[False, False, True], inplace=True)
    results.drop_duplicates(subset=['Ci', '小区名称', 'Lon', 'Lat', 'bandname'], keep='first', inplace=True)
    results = pd.merge(results, Bandcenter, on='bandname', how='left')

    results['toCdirection'] = [Get_Angle(results.iloc[i][['Lat', 'Lon','centerlat', 'centerlon']].values) for i in
                               range(len(results))]
    results['directionD'] = [min([abs(results.iloc[i]['toCdirection'] - results.iloc[i]['Ang']),
                      abs(results.iloc[i]['toCdirection']  - results.iloc[i]['Ang'] - 360),
                      abs(results.iloc[i]['toCdirection']  - results.iloc[i]['Ang'] + 360)]) for i in
                               range(len(results))]

    results.loc[((150 >= results['distance']) & (results['directionD'] < 120)) | \
                    ((300 >= results['distance']) & (results['distance'] > 150) & (
                            results['directionD'] < 90)) | \
                    ((400 >= results['distance']) & (results['distance'] > 300) & (
                            results['directionD'] < 60)) | \
                    ((500 >= results['distance']) & (results['distance'] > 400) & (
                            results['directionD'] < 45)) | \
                    ((600 >= results['distance']) & (results['distance'] > 500) & (
                            results['directionD'] < 30)) | \
                    ((800 >= results['distance']) & (results['distance'] > 600) & (
                            results['directionD'] < 15)),'nearselect']='select'

    results.loc[results.nearselect==np.nan,'nearselect']='noselect'

    try:
        inbandpoint['distance'] = 0
        inbandpoint['centerlat'] = 0
        inbandpoint['centerlon'] = 0
        inbandpoint['toCdirection'] = 0
        inbandpoint['directionD'] = 0
        inbandpoint['nearselect'] = 'select'
        results = pd.concat([results, inbandpoint], axis=0)
    except:
        print('边框内无小区')






    return  results




def Nearpointcell(threeinfo):
    # gruopbandnametemp = list(set(band['Name']))[0]
    # for bandid in range(len(band)):
    #POINT 格式 Lat Lon
    # cell, point, getnum
    # bandpointlatlon = list(band.iloc[bandid][['lat', 'lon']].values)

    tree = KDTree(threeinfo[0][['Lat', 'Lon']])
    cellout = tree.query(threeinfo[1], k=threeinfo[2])

    # distance = cellout[0].flatten() * 111.11 * 1000
    # print(distance)
    cellmark= cellout[1].flatten()
    # 生成临近点距离、index列表
    # print(cellmark)
    pointinfo = np.array([threeinfo[1]] * len(cellmark))
    # 转置并去重
    LOONear = threeinfo[0].iloc[cellmark, :]
    # 提取从非边界内小区中提出临近的datafram表

    Coluin = threeinfo[0].columns.values.tolist()

    if threeinfo[3]=='yes':

        LOONear = np.hstack((np.array(LOONear), pointinfo))
        Coluin.append('pointLat')
        Coluin.append('pointLon')

    return pd.DataFrame(LOONear,columns=Coluin)



def getGcentre(bandmap):
    area = 0.0
    # 多边形面积
    Gx = 0.0
    Gy = 0.0
    # 重心的x、y
    bandsize = len(bandmap)
    for i in range(0, bandsize):
        print(i % bandsize)
        iLatiLng = bandmap[['Lat', 'Lon']].iloc[i % bandsize].to_list()
        nextLatLng = bandmap[['Lat', 'Lon']].iloc[i - 1].to_list()
        temp = (iLatiLng[0] * nextLatLng[1] - iLatiLng[1] * nextLatLng[0]) / 2.0
        area += temp
        Gx += temp * (iLatiLng[0] + nextLatLng[0]) / 3.0
        Gy += temp * (iLatiLng[1] + nextLatLng[1]) / 3.0
    Gx = Gx / area
    Gy = Gy / area
    return pd.DataFrame([[list(set(bandmap['Name']))[0], Gx, Gy]], columns=['bandname', 'centerlat', 'centerlon'])


def Cellfilter(Ltecell):
    rjtcolor = ['#DC143C', '#0000FF', '#3CB371', '#FFFF00']
    Ltecell.fillna(0, inplace=True)
    Ltecell.replace('', 0, inplace=True)
    Ltecell.replace('Timestamp', '', inplace=True)
    Ltecell = Ltecell[(Ltecell.Lon > 0) & (Ltecell.Lat > 0)]
    # Ltecell['小区名称']=Ltecell['小区名称'].str.replace('-','')
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    Ltecell[['Lat', 'Lon', 'Ang']] = Ltecell[['Lat', 'Lon', 'Ang']].astype(float)
    Ltecell['Ci'] = Ltecell['Ci'].apply(int)
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    # 增加区分室分的type列
    Ltecell['type'] = Ltecell.小区名称.apply(lambda x: 'indoor' if 'SF' in x or '室分' in x else 'outdoor')
    Ltecell = Ltecell[~Ltecell.小区名称.str.contains('NB')]

    Ltecellcmap = {Ltecell.iloc[i]['小区名称']: randomcolor(rjtcolor) for i in range(len(Ltecell))}
    return Ltecell,Ltecellcmap


def Get_distance_point(LatLonDD):
    """
    根据经纬度，距离，方向获得一个地点 lat,lon,directionO,directionD, distance
    :param distance: 距离（千米）
    :source:纬度,经度,direction: 方向（北：0，东：90，南：180，西：360）
    :return:目标经纬度：[纬度,经度]
    """
    if LatLonDD[3]=='不调整':
        return [LatLonDD[0], LatLonDD[1]]
    else:
        start = geopy.Point(LatLonDD[0], LatLonDD[1])
        d = geopy.distance.VincentyDistance(kilometers=LatLonDD[4])
        return list(d.destination(point=start, bearing=LatLonDD[2]+LatLonDD[3]))[0:2]



def Createcellband(Ltecell):
    """

    :param pandascell:
    :return:
    """
    Ltecell.fillna(0, inplace=True)
    Ltecell.replace('', 0, inplace=True)
    Ltecell.replace('Timestamp', '', inplace=True)
    Ltecell = Ltecell[(Ltecell.Lon > 0) & (Ltecell.Lat > 0)]
    # Ltecell['小区名称']=Ltecell['小区名称'].str.replace('-','')
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    Ltecell[['Lat', 'Lon', 'Ang']] = Ltecell[['Lat', 'Lon', 'Ang']].astype(float)
    Ltecell['Ci'] = Ltecell['Ci'].apply(int)
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    # 增加区分室分的type列
    Ltecell['type'] = Ltecell.小区名称.apply(lambda x: 'indoor' if 'SF' in x or '室分' in x else 'outdoor')

    colus=Ltecell.columns.values.tolist()
    basecellall=Ltecell.values.tolist()
    cellall=basecellall*13
    cellall=sorted(cellall)
    cellall=pd.DataFrame(cellall,columns=colus)

    print(cellall.head(10))
    print(len(cellall))
    numlist=list(range(0,12))
    numlist.append(0)
    numall=numlist*len(Ltecell)
    numall=pd.DataFrame(numall,columns=['adjust'])
    print(numall)
    Ltecellband=pd.concat([cellall,numall],axis=1)
    Ltecellband['adjust']=Ltecellband.adjust.apply(lambda x:'不调整' if x==0 else -30+(x-1)*6)
    Ltecellband['distance']=0.1
    pool=Pool(200)
    resuts=pool.map(Get_distance_point,Ltecellband[['Lat','Lon','Ang','adjust','distance']].values.tolist())
    pool.close()
    pool.join()
    print(resuts)

    resuts=pd.DataFrame(resuts,columns=['bandLat','bandLon'])

    Ltecellband=pd.concat([Ltecellband,resuts],axis=1)
    return Ltecellband

def  LinepointDreduce(linepoint,subnum):
    # 线上的点降维
    # 构造分段的gj数据点
    angles = [90]
    for i in range(len(linepoint) - 1):
        info = Geodesic.WGS84.Inverse(
            linepoint.iloc[i]['Lat'], linepoint.iloc[i]['Lon'],
            linepoint.iloc[i + 1]['Lat'], linepoint.iloc[i + 1]['Lon']
        )
        angles.append(info['azi2'])
    print(angles)

    # Change from CW-from-North to CCW-from-East.
    angles = np.deg2rad(450 - np.array(angles))

    # Normalize the speed to use as the length of the arrows.
    r = 1
    linepoint['u'] = r * np.cos(angles)
    linepoint['v'] = r * np.sin(angles)

    fig, ax = plt.subplots()
    linepoint = linepoint.dropna()

    # This style was lost below.
    ax.plot(
        linepoint['Lon'],
        linepoint['Lat'],
        color='darkorange',
        linewidth=5,
        alpha=0.5
    )

    # This is preserved in the SVG icon.
    sub = subnum
    kw = {'color': 'deepskyblue', 'alpha': 0.8, 'scale': 10}
    ax.quiver(linepoint['Lon'][::sub],
              linepoint['Lat'][::sub],
              linepoint['u'][::sub],
              linepoint['v'][::sub], **kw)

    gj = mplleaflet.fig_to_geojson(fig=fig)
    # 构造分段的gj数据点
    Dpoint=[]
    for feature in gj['features']:
        if feature['geometry']['type'] == 'LineString':
            continue
        elif feature['geometry']['type'] == 'Point':
            lon, lat = feature['geometry']['coordinates']
            Dpoint.append([lat,lon])

    return pd.DataFrame(Dpoint,columns=['Lat','Lon'])

            # 线上的点降维