import os,sys
import datetime
import uuid
import random
import numpy as np
import shutil
from skimage.measure import find_contours
from matplotlib.patches import Polygon
import math as Math


try:
    import http.client as httplib
except Exception as e:
    import httplib
    print(str(e) + "Python 2 Mode")
from PIL import Image

def str_to_byte(o):
    bytes_ = str(o.encode()).replace("b'","")
    count = 0
    pass_ = 0
    for byte in bytes_:
        if pass_!=0:
            pass_-=1
            continue
        if byte == '\\':
            pass_=11
            count+=1
        count+=1
    return count -1

def isNone(s):
    if s is None:
        return True
    elif type(s) == str:
         if s == "":
             return True
    return False

def default_DICT_TO_JSON(o):
    if isinstance(o, np.int8): return int(o)  
    if isinstance(o, np.int16): return int(o)  
    if isinstance(o, np.int32): return int(o)  
    if isinstance(o, np.int64): return int(o)  


def data_to_polygon(x, y, direction, distance, view_angle):
    times = 1
    x4 = x
    y4 = y

    x2 = x + distance * 2 / Math.sqrt(3) * Math.sin(Math.radians(direction + view_angle / 2)) * times
    y2 = y + distance * 2 / Math.sqrt(3) * Math.cos(Math.radians(direction + view_angle / 2)) * times

    x3 = x + distance * 2 / Math.sqrt(3) * Math.sin(Math.radians(direction - view_angle / 2)) * times
    y3 = y + distance * 2 / Math.sqrt(3) * Math.cos(Math.radians(direction - view_angle / 2)) * times

    return "POLYGON((" + str(x4) + " " + str(y4) + ", " + str(x2) + " " + str(y2) + ", " + str(x3) + " " + str(
        y3) + ", " + str(x4) + " " + str(y4) + "))"

def result_to_polygon_name(re, classes, option='polygon'):
    data = {"annotation_result":[]}
    points=None
    if option == "polygon":
        points = np_to_polygon(re["masks"])
    else:
        option = "bbox"
        points = re['rois'].tolist()
    cnt_ids = len(re['class_ids'])
    for idx in range(cnt_ids):
        try:
            annotation_result={}
            annotation_result.update({"object_type":classes[re['class_ids'][idx]]})
            annotation_result.update({"draw_type":option})
            annotation_result.update({"points":points[idx]})
            annotation_result.update({"id":re['class_ids'][idx]})
            annotation_result.update({"score":float(re['scores'][idx])})
            data['annotation_result'].append(annotation_result)
        except Exception as e:
            print("NO LOG :    - ",idx," : Pass! (",e,")")
    if "count" in (re.keys()):
        data.update({"annotation_count": re["count"]})
    return data

def results_to_polygon_name(res, classes):
    result=[]
    for re in res:
        try:
            result.append(result_to_polygon_name(re,classes))
        except:
            continue
    return result


def url_parse(url):
    domain = url.split("/")[0]
    get = url.split(domain)[-1]
    return domain, get


def create_folder(path):
    path = set_path(path)
    if path[-1] == '/':
        path = path[0:len(path)-1]
    try:
        if os.path.isdir(path) is False:
            os.mkdir(path)
    except Exception as e:
        print("create Folder : ", e)
        repath = str(path).split("/")[-1]
        repath = str(path).split("/"+repath)[0]
        create_folder(repath)
        create_folder(path)
    if path[-1] is not '/':
        path = path+"/"
    return path


def create_colors(n):
    colors = []
    for i in range(n + 1):
        color = (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))
        colors.append(color)
    return colors


def create_name(file_format, path=None):
    file_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = file_name.replace(":", "").replace(" ", "").replace("-", "")
    if path:
        if os.path.isfile(path+file_name):
            return create_name(file_format, path)
    return file_name + uuid.uuid4().hex + "." + file_format


def set_path(path):
    path = path.replace("\\", "/")
    if path[0] != '/' and path[1] != ':':
        path = os.getcwd().replace("\\", "/") + "/" + path
    return path


def set_mask(ori, cpy, color):
    x, y, z = cpy.shape
    _, _, o = ori.shape
    for i in range(z):
        for j in range(o):
            a = cpy[:, :, i]
            b = color[i][j]
            k = a * b
            ori[:, :, j] = ori[:, :, j] + k
    return ori


def get_exif(ratio, ref):
    if ratio.tag == 17:
        data = str(ratio).split("/")
        a = float(data[0])
        b = float(data[1])
        data = a / b
    elif ratio.tag == 4 or ratio.tag == 2:
        item = ratio.values
        last = str(item[2]).split("/")
        if len(last) != 1:
            deg = float(last[0])/float(last[1])
        else:
            deg = float(str(item[2]))
        tmin = float(str(item[0]))
        tsec = float(str(item[1]))
        data = (tmin + (tsec + deg / 60.0) / 60.0)
        if ratio.tag == 2:
            if str(ref) == 'S':
                data *= -1
        if ratio.tag == 4:
            if str(ref) == 'W':
                data *= -1
    return data


def get_page(protocol, domain, get):
    conn = None
    if protocol == "https":
        conn = httplib.HTTPSConnection(domain)
    elif protocol == "http":
        conn = httplib.HTTPConnection(domain)
    if conn is not None:
        conn.request("GET", get)
        page = conn.getresponse()
        return page.read()
    else:
        return None


def get_count(result, class_names):
    res = {}
    if 'class_ids' in result.keys():
        classids = result['class_ids']
        for cid in classids:
            name = class_names[cid]
            if name in res.keys():
                res[name] += 1
            else:
                res[name] = 1
    return res


def download_image(url, to_path):
    protocol = url.split("://")
    ext_list = ['jpg', 'JPG', 'png', 'PNG', 'gif', 'GIF', 'bmp', 'BMP']
    file_ext = url.split(".")[-1]
    if file_ext in ext_list:
        file_name = create_name(file_ext)
    else:
        file_name = create_name('jpg')
    if 'http' in protocol[0] or 'https' in protocol[0]:
        domain, get = url_parse(protocol[1])
        page = get_page(protocol[0], domain, get)
        if page is not None:
            fail = open(to_path + file_name, "wb")
            fail.write(page)
            fail.close()
            r_url = file_name
        else:
            r_url = None
    elif 'file' in protocol[0]:
        try:
            shutil.copy(protocol[1], to_path + file_name)
            r_url = file_name
        except Exception as e:
            print(str(e) + " Error")
            r_url = None
    else:
        r_url = url
    return r_url


def image_rotation(image, ori):
    ori = ori.values
    try:
        if 2 in ori:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif 3 in ori:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif 4 in ori:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif 5 in ori:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
            image = image.transpose(Image.ROTATE_90)
        elif 6 in ori:
            image = image.transpose(Image.ROTATE_270)
        elif 7 in ori:
            image = image.transpose(Image.ROTATE_90)
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif 8 in ori:
            image = image.transpose(Image.ROTATE_270)
    except Exception as ex:
        raise "image Rotation ERROR"
    return image


def np_to_polygon(masks):
    # Number of instances
    data = []
    num = masks.shape[-1]
    for i in range(num):
        # Mask
        mask = masks[:, :, i]
        padded_mask = np.zeros(
            (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        contours = find_contours(padded_mask, 0.5)
        for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            data.append(Polygon(verts).get_path().vertices)
    return simply_polygon(data)


def simply_polygon(polygons):
    simply = []
    for polygon in polygons:
        tpoint = None
        points = []
        for point in polygon:
            if tpoint is None:
                tpoint = point
                points.append(tpoint.tolist())
            else:
                if tpoint[0] != point[0] and tpoint[1] != point[1]:
                    points.append(tpoint.tolist())
                tpoint = point
        if points[0][0] != points[-1][0] and points[0][1] != points[-1][1]:
            points.append(points[0])
        simply.append(points)
    return simply


def datatime_to_timestamp(date_time):
    tt = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return int(tt.timestamp())


def convert_to_float(o):
    o = str(o)
    try:
        o = int(o)
    except:
        pass
    if isinstance(o, int):
        return float(str(o))
    elif isinstance(o, float):
        return o
    else:
        last = str(o).split("/")
        return float(last[0])/float(last[1])

def exif_to_data(ratio, ref=None):
    if ratio.tag == 17:
        data = str(ratio).split("/")
        a = convert_to_float(data[0])
        b = convert_to_float(data[1])
        data = a / b
    elif ratio.tag == 4 or ratio.tag == 2:
        item = ratio.values
        min = convert_to_float(item[0])
        sec = convert_to_float(item[1])
        deg = convert_to_float(item[2])
        data = (min + (sec + deg / 60.0) / 60.0)
        if data == 0.0:
            data = None
        if ref is not None:
            if str(ref) == 'S' or str(ref) == 'W':
                data *= -1        
    elif ratio.tag == 6:
        data = convert_to_float(ratio.values[0])
    else:
        data = None
    return data

def check_format_date(o):
    # 1970-01-01 00:00:00
    datetime_ = o.split(' ')
    date = datetime_[0].split('-')
    time = datetime_[1].split(':')
    if int(date[1]) > 12 or int(date[1]) < 1:
        date[1] = "01"
    if int(date[2]) > 31 or int(date[2]) < 1:
        date[2] = "01"
    if int(time[0]) > 24 or int(time[0]) < 0:
        time[0] = "00"
    if int(time[1]) > 60 or int(time[1]) < 0:
        time[1] = "00"
    if int(time[2]) > 60 or int(time[2]) < 0:
        time[2] = "00"
    return date[0]+"-"+date[1]+"-"+date[2]+" "+time[0]+":"+time[1]+":"+time[2]

def getCountFile(path):
    list_of_files = os.listdir(path)
    return len(list_of_files)

def polygonToXY(points):
    x_list = []
    y_list = []
    for p in points:
        x_list.append(p[0])
        y_list.append(p[1])
    x_max = max(x_list)
    y_max = max(y_list)
    x_min = min(x_list)
    y_min = min(y_list)
    avgX = (x_max + x_min) / 2
    avgY = (y_max + y_min) / 2
    distance = (x_max-x_min,y_max-y_min)
    center_point = (avgX,avgY)
    info_dic = {'distance': distance,'center_point':center_point, 'diagonal':[x_max,y_max,x_min,y_min]}
    return info_dic

def AddPolygonXY(ori_data):
    for ori_data_idx in range(len(ori_data)):
        image = ori_data[ori_data_idx]
        annotation_result = image['annotation_result']
        for annotation_result_idx in range(len(annotation_result)):
            result = annotation_result[annotation_result_idx]
            XY=polygonToXY(result['points'])
            ori_data[ori_data_idx]['annotation_result'][annotation_result_idx].update({'xy':XY})
    return ori_data