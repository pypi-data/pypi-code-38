#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 常用通用基础函数
from __future__ import print_function
import os
import sys
import platform
import subprocess
import time
import json
import math
import shutil
import logging
import traceback
import copy
import hashlib
import pickle
import gzip
import cv2
import yaml
import string
import smtplib
import tempfile
import wave
import inspect
import numpy as np
from PIL import Image
from PIL import ImageOps
from xpinyin import Pinyin
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dp import audio
#from pytz import timezone

CUR_PATH = os.path.dirname(os.path.abspath(__file__))

NUMERALS = {u'零': 0, u'一': 1, u'二': 2, u'两': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'十': 10, u'百': 100, u'千': 1000, u'万': 10000, u'亿': 100000000}
TMPNAMES = ['.DS_Store', 'unknow', 'tmp']

pinyin = Pinyin()


def init_logging(log_file="sys", log_path='/tmp', log_level=logging.DEBUG):
    """初始化默认日志参数"""
    mkdir(log_path + '/log')
    logging.basicConfig(level=log_level,
                        format='[%(levelname)s]\t%(asctime)s:%(relativeCreated)d\t%(filename)s:%(lineno)d\t%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_path + "/log/" + log_file + "." + time.strftime('%Y%m%d%H', time.localtime()) + ".log",
                        filemode='a')
    logging.info("__init_logging__")


def get_trace():
    """获得异常栈内容"""
    try:
        errmsg = "Traceback (most recent call last):\n "
        exc_type, exc_value, exc_tb = sys.exc_info()
        for filename, linenum, funcname, source in traceback.extract_tb(exc_tb):
            errmsg += "  File \"%-23s\", line %s, in %s() \n\t  %s \n" % (filename, linenum, funcname, source)
        errmsg += str(exc_type.__name__) + ": " + str(exc_value)
        # traceback.print_exc()
    except:
        traceback.print_exc()
        errmsg = ''
    return errmsg


def mkdir(path):
    """检查并创建目录"""
    if not os.path.exists(path):
        os.makedirs(path)


def rmdir(path, skips=None):
    """删除目录"""
    # print(path)
    if not os.path.exists(path):
        return
    if os.path.isfile(path):  # 文件
        if skips is None or path not in skips:
            # os.unlink(path)
            os.remove(path)
    elif os.path.isdir(path):  # 目录
        '''for file in os.listdir(path):
            # print(path +'/'+ file)
            rmdir(path + '/' + file, skips=skips)'''
        if skips is None or path not in skips:
            # os.rmdir(path)
            shutil.rmtree(path)


def rm(filename):
    """删除文件"""
    # print(filename)
    if os.path.exists(filename):
        # os.unlink(filename)
        os.remove(filename)


def cp(source_file, target_file, remove=False):
    """复制文件"""
    ret = False
    if not os.path.exists(target_file) or (os.path.exists(target_file) and os.path.getsize(target_file) != os.path.getsize(source_file)):
        #ret = open(target_file, "wb").write(open(source_file, "rb").read())
        ret = shutil.copyfile(source_file, target_file)
    if remove is True:
        if os.path.exists(target_file) and os.path.getsize(target_file) == os.path.getsize(source_file):  # 确保目标文件与源文件完全一致才能删源文件
            #ret = os.unlink(source_file)
            ret = os.remove(source_file)
    return ret


def mv(source_file, target_file):
    """移动文件"""
    return cp(source_file, target_file, remove=True)


def play_sound(media='', filename='', callback=None):
    """播放声音（默认声音为报警音）"""
    if filename == '' and media == '':
        filename = CUR_PATH + '/data/media/warning.wav'
    elif media != '':
        filename = CUR_PATH + '/data/media/' + media
    # print(filename)
    player = audio.Player()
    player.play(filename, onCompleted=callback)


def get_today():
    """获得今天日期"""
    return time.strftime("%Y-%m-%d", time.localtime())


def get_date(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """返回时间戳对应的格式化日期格式"""
    x = time.localtime(float(timestamp))
    return time.strftime(format, x)


def md5(string):
    """生成md5"""
    if isinstance(string, list):
        string = copy.deepcopy(string)
        for i in range(len(string)):
            string[i] = md5(string[i])
            if string[i] == '':
                return ''
                # print string
    elif isinstance(string, (str, float, int)):
        try:
            string = str(string)
            string = hashlib.md5(string.encode(encoding='UTF-8')).hexdigest()
        except:
            logging.error('md5 fail! [' + string + ']\n' + get_trace())
            return ''
    return string


def pickle_dump(object, filename, protocol=0):
    """对象压缩后保存到文件"""
    file = gzip.GzipFile(filename, 'wb')
    file.write(pickle.dumps(object, protocol))
    file.close()


def pickle_load(filename):
    """加载保存的压缩对象文件->"""
    file = gzip.GzipFile(filename, 'rb')
    buffer = ""
    while True:
        data = file.read()
        if data == "":
            break
        buffer += data
    object = pickle.loads(buffer)
    file.close()
    return object


def load_data(filename, split=None, loadjson=False, callback=None):
    """加载词典"""
    data = []
    # print filename
    fo = None
    try:
        fo = open(filename, 'r')
        if fo is None:
            return data
        for line in fo:
            line = line.strip()
            if len(line) == 0:
                continue
            if loadjson is True:
                line = json.loads(line)
            elif type(split) is str:
                line = line.split(split)
            if inspect.isfunction(callback):
                callback(line)
            else:
                data.append(line)
    finally:
        if fo:
            fo.close()
    # logging.info("load_dict: [" + filename + "][" + str(len(data)) + "]")
    return data


def gen_token(appid, uid, secret_key, token_type='11'):
    """生成token"""
    timestamp = str(int(time.time()))
    # timestamp = '1469618708'
    sign = md5(timestamp + str(uid) + str(appid) + str(secret_key))
    return token_type + '.' + sign + '.' + timestamp + '.' + str(uid) + "-" + str(appid)


def get_video_info(filename):
    """获得视频的fps帧率（即每秒传输帧数）、总帧数、时长等信息"""
    # logging.info('__get_video_info__ {}'.format(filename))
    video_info = {
        'fps': 0.0,  # 帧率
        'sum': 0,  # 总帧数
        'seconds': 0,  # 总秒数
        'width': 0,  # 分辨率-宽
        'height': 0,  # 分辨率-高
        'len': '00:00:00'  # 格式化时长
    }
    if not os.path.exists(filename):
        return video_info
    video = cv2.VideoCapture(filename)
    video_info['width'] = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_info['height'] = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # get fps帧率
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    if int(major_ver) < 3:
        video_info['fps'] = video.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
        video_info['fps'] = video.get(cv2.CAP_PROP_FPS)
    # logging.info('{} {}'.format(filename, video_info['fps']))

    # get sum cap总帧数
    video_info['sum'] = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    '''
    while (True):
        ret, frame = video.read()
        if ret is False:
            break
        video_info['sum'] = video_info['sum'] + 1
    '''
    video.release()

    # 计算视频总时长
    video_info['seconds'] = video_info['sum'] / video_info['fps']
    video_info['len'] = format_video_length(video_info['seconds'])

    # logging.info('get_video_info res: {}'.format(video_info))
    return video_info


def format_video_length(seconds):
    """格式化视频长度格式（秒数 -> h:m:s格式）"""
    seconds = math.ceil(seconds)  # 向上取整
    s = int(seconds % 60)
    m = int(seconds // 60 % 60)
    h = int(seconds // 60 // 60)
    return '%02d:%02d:%02d' % (h, m, s)


def get_path_filecount(path):
    """获得目录下的文件个数"""
    cmd = 'ls {} |wc -l'.format(path)
    # logging.info(cmd)
    output = os.popen(cmd)
    cnt = output.read().strip()
    # logging.info(cnt)
    return int(cnt)


def get_file_rowcount(filename):
    """获得文件的行数"""
    cmd = 'wc -l {}'.format(filename)
    # logging.info(cmd)
    output = os.popen(cmd)
    cnt = output.read().strip().split()
    # logging.info(cnt)
    try:
        return int(cnt[0])
    except:
        return -1


def image_reader_creator(img_path, height, width, rgb=False, reshape1=False, label_split_dot=0, label_split_midline=1, label_list=[]):
    """自定义image目录文件列表reader"""

    def reader():
        imgs = os.listdir(img_path)
        for i in range(len(imgs)):
            if imgs[i] in TMPNAMES:
                continue
            # imgs[i] = '0-5.png'
            # print(imgs[i])
            label = imgs[i].split('.')[label_split_dot]
            if label_split_midline >= 0:
                label = label.split('-')[label_split_midline]
            if type(label_list) is list and len(label_list) > 0:
                label = label_list.index(label)
            if rgb:
                image = load_rgb_image(img_path + imgs[i], height, width)
                # print(image.shape)  #(1, 3, 32, 32)
                image = image[0]
                # print(img_path + imgs[i])
                if reshape1:  # 多维转1维
                    image = image.reshape(-1)
                    # print(image.shape) (3072,)
                # print('{} {} {}'.format(img_path + imgs[i], label, image))
                yield image, int(label)
            else:
                image = load_image(img_path + imgs[i], height, width)
                # print(img_path + imgs[i])
                # print('{} {} {}'.format(img_path + imgs[i], label, image[0][0]))
                yield image[0][0], int(label)

    return reader


def load_rgb_image(img_path, height=32, width=32):
    """加载rgb图片数据"""
    im = Image.open(img_path)
    im = im.resize((height, width), Image.ANTIALIAS)
    im = np.array(im).astype(np.float32)
    # print(im)
    # print(im.shape)    #(32, 32, 3)
    # The storage order of the loaded image is W(width),H(height), C(channel). PaddlePaddle requires the CHW order, so transpose them.
    im = im.transpose((2, 0, 1))  # CHW
    im = im / 255.0
    # print(im.shape)    #(3, 32, 32)

    # Add one dimension to mimic the list format.
    im = np.expand_dims(im, axis=0)
    # print(im.shape)   load_rgb_image #(1, 3, 32, 32)
    return im


def load_image(img_path, height, width, rotate=0, invert=False, sobel=False, ksize=5, dilate=0, erode=0, save_resize=False, mid_imgs=[]):
    """加载黑白图片数据"""
    base_path = os.path.dirname(img_path) + '/'
    if sobel:  # 边缘检测
        img_path = image_sobel(img_path, ksize=ksize, dilate=dilate, erode=erode, mid_imgs=mid_imgs)
    # 加载图片
    im = Image.open(img_path).convert('L')
    # 缩略图
    im = im.resize((height, width), Image.ANTIALIAS)
    # 旋转
    if rotate != 0:  # 旋转度数
        im = im.rotate(rotate)
    # 反转颜色(不要跟sobel一起用，因为sobel已经自动转为黑底+白边缘了)
    if invert:
        im = ImageOps.invert(im)
    # 临时保存
    if save_resize:
        name = img_path.split('/')[-1]
        # resize_path = img_path.replace(name,'') + '../tmp/' + name.split('.')[0]+"_"+str(height)+"x"+str(width)+"."+name.split('.')[1]
        mkdir(base_path + 'tmp/')
        resize_path = base_path + 'tmp/' + name.split('.')[0] + "_" + str(height) + "x" + str(width) + "." + name.split('.')[1]
        print(resize_path)
        im.save(resize_path)
        mid_imgs.append(resize_path)
    # 返回数据
    im = np.array(im).reshape(1, 1, height, width).astype(np.float32)  # [N C H W] N几张图;C=1灰图;H高;W宽
    im = im / 255.0 * 2.0 - 1.0
    return im


def image_sobel(img_path, ksize=5, dilate=0, erode=0, dilate2=0, mid_imgs=[]):
    """图片边缘检测"""
    img = cv2.imread(img_path)
    # 灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # write_image(gray, img_path, 'gray')
    # 高斯平滑
    gaussian = cv2.GaussianBlur(gray, (3, 3), 0, 0, cv2.BORDER_DEFAULT)
    # write_image(gaussian, img_path, 'gaussion')
    # 中值滤波
    median = cv2.medianBlur(gaussian, 5)
    # write_image(median, img_path, 'median')
    # Sobel算子，X方向求梯度,对图像进行边缘检测
    sobel = cv2.Sobel(median, cv2.CV_8U, 1, 0, ksize=ksize)  # ksize:1/3/5/7   cv2.CV_8U/cv2.CV_16S
    # sobel = cv2.Sobel(median, cv2.CV_16S, 1, 0, ksize=ksize) #ksize:1/3/5/7   cv2.CV_8U/cv2.CV_16S
    sobel = cv2.convertScaleAbs(sobel)
    # 二值化
    ret, binary = cv2.threshold(sobel, 170, 255, cv2.THRESH_BINARY)
    threshold_path = write_image(binary, img_path, 'threshold')
    mid_imgs.append(threshold_path)
    if dilate == 0 and erode == 0:
        return threshold_path
    else:
        # 膨胀和腐蚀操作的核函数
        element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
        element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 7))
        # 膨胀一次，让轮廓突出
        dilation = cv2.dilate(binary, element2, iterations=dilate)  # iterations=1
        dilation_path = write_image(dilation, img_path, 'dilation')
        mid_imgs.append(dilation_path)
        if erode > 0:  # 腐蚀，去掉细节
            dilation = cv2.erode(dilation, element1, iterations=erode)  # iterations=1
            dilation_path = write_image(dilation, img_path, 'erosion')
            mid_imgs.append(dilation_path)
        if dilate2 > 0:  # 再次膨胀，让轮廓明显一些
            dilation2 = cv2.dilate(dilation, element2, iterations=dilate2)  # iterations=3设置太大但车牌区域很小时非车牌区域容易边缘连片过度，设置太小但车牌占比过大时容易省简称和后边连不上
            dilation_path = write_image(dilation2, img_path, 'dilation2')
            mid_imgs.append(dilation_path)
        return dilation_path


def write_image(img, filename, step='', path='./upload/tmp'):
    """保存图片并打印"""
    # print(name)
    mkdir(path)
    img_file = path + '/' + filename
    if step != '':
        img_file = path + '/' + filename.split('.')[0] + '_' + step + '.' + filename.split('.')[-1]
    cv2.imwrite(img_file, img)
    # print(img_file)
    return img_file


def qrcode_detect(img=None, img_file='', debug_path=''):
    """图片二维码位置检测"""
    if img is None and os.path.exists(img_file) is False:
        return (), 'param img empty or not exists!', []
    # 0.加载图片
    if img is None:
        img = cv2.imread(img_file)
    # 1.先将读入的摄像头frame转换成灰度图：
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2.使用opencv自带的Sobel算子进行过滤：
    gradX = cv2.Sobel(gray, cv2.CV_32F, 1, 0, -1)
    gradY = cv2.Sobel(gray, cv2.CV_32F, 0, 1, -1)
    # 具体参数可参考：http://blog.csdn.net/sunny2038/article/details/9170013

    # 3.将过滤得到的X方向像素值减去Y方向的像素值：
    gradient = cv2.subtract(gradX, gradY)

    # 4.先缩放元素再取绝对值，最后转换格式为8bit型
    gradient = cv2.convertScaleAbs(gradient)

    # 5.均值滤波取二值化：
    blurred = cv2.blur(gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 160, 160, cv2.THRESH_BINARY)

    # 6.腐蚀和膨胀的函数：
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)
    if debug_path is not None and len(debug_path) > 0:
        cv2.imwrite(debug_path + '/dilate.png', closed)

    # 7.找到边界findContours函数
    cnts, hierarchy = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print(res)
    # binary,cnts,hierarchy = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    # 8.计算出包围目标的最小矩形区域：
    c = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
    rect = cv2.minAreaRect(c)
    sbox = np.int0(cv2.boxPoints(rect))

    # 9.计算二维码位置及打码范围
    min = np.min(sbox, axis=0)
    max = np.max(sbox, axis=0)
    x1, y1, x2, y2, w, h = min[0], min[1], max[0], max[1], max[0] - min[0], max[1] - min[1]
    qrbox = x1, y1, x2, y2  # 二维码位置
    x1 = x1 - int(round(w * 0.6))
    y1 = y1 - int(round(h * 0.5))
    x2 = x2 + int(round(w * 0.6))
    y2 = y2 + int(round(h * 0.75))
    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0
    debox = x1, y1, x2, y2  # 打码位置(二维码一般上下有文案)
    # print(sbox,qrbox,debox)
    if debug_path is not None and len(debug_path) > 0:
        cv2.rectangle(img, (qrbox[0], qrbox[1]), (qrbox[2], qrbox[3]), (255, 0, 0), 2)
        cv2.rectangle(img, (debox[0], debox[1]), (debox[2], debox[3]), (0, 255, 0), 2)
        cv2.imwrite(debug_path + '/out.png', img)

    return qrbox, debox, sbox


def get_pinyin(s, split='', tone_marks='', shengmu=False):
    """获得汉字的拼音
    Params:
        split   单字分割符
        tone_marks  返回声调(marks：shàng-hǎi，numbers：shang4-hai3，为空时不反回声调)
        shengmu 只返回声母
    """
    if shengmu is False:  # 全拼
        if tone_marks.strip() == '':
            return pinyin.get_pinyin(s, split)
        else:
            return pinyin.get_pinyin(s, split, tone_marks=tone_marks)
    else:  # 仅声母
        return pinyin.get_initials(s, split).lower()


def get_shengmu(s, split=''):
    """返回汉子的拼音声母"""
    return get_pinyin(s, split, shengmu=True)


def load_conf(filename, format='yaml'):
    """加载配置文件为dict"""
    try:
        with open(filename, "r") as f:
            if format == 'yaml':
                return yaml.safe_load(f)
            elif format == 'json':
                return json.loads(f.read())
    except Exception as e:
        logging.error("load conf fail! {} {}".format(filename, e))


def dump_conf(data, filename, format='yaml'):
    """保存dict为配置文件"""
    try:
        with open(filename, "w") as f:
            if format == 'yaml':
                yaml.dump(data, f, default_flow_style=False)
            elif format == 'json':
                json.dump(data, f)
    except Exception as e:
        logging.error("dump conf fail! {} {}".format(filename, e))
        return False

    return True


def send_mail(subject, body, attach_list, to, user, sender,
              password, smtp_server, smtp_port):
    """
    发送邮件

    :param subject: 邮件标题
    :param body: 邮件正文
    :param attach_list: 附件
    :param to: 收件人
    :param user: 发件人
    :param sender: 发件人信息
    :param password: 密码
    :param smtp_server: smtp 服务器
    :param smtp_port: smtp 端口号
    :returns: True: 发送成功; False: 发送失败
    """
    txt = MIMEText(body.encode('utf-8'), 'html', 'utf-8')
    msg = MIMEMultipart()
    msg.attach(txt)

    for attach in attach_list:
        try:
            att = MIMEText(open(attach, 'rb').read(), 'base64', 'utf-8')
            filename = os.path.basename(attach)
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename="%s"' % filename
            msg.attach(att)
        except Exception:
            logging.error(u'附件 %s 发送失败！' % attach)
            continue

    msg['from'] = sender
    msg['to'] = to
    msg['subject'] = subject

    try:
        session = smtplib.SMTP()
        session.connect(smtp_server, smtp_port)
        session.starttls()
        session.login(user, password)
        session.sendmail(sender, to, msg.as_string())
        session.close()
        return True
    except Exception as e:
        logging.error(e)
        return False


def get_file_content(filename):
    """
    读取文件内容并返回
    :param filename: 文件路径
    :returns: 文件内容
    :raises IOError: 读取失败则抛出 IOError
    """
    with open(filename, 'rb') as fp:
        return fp.read()


def write_temp_file(data, suffix):
    """ 
    写入临时文件
    :param data: 二进制数据
    :param suffix: 后缀名
    :returns: 文件保存后的路径
    """
    filename = ''
    mode = 'w+b'
    if type(data) is str:
        mode = 'w'
    with tempfile.NamedTemporaryFile(mode=mode, suffix=suffix, delete=False) as f:
        f.write(data)
        filename = f.name
    return filename


def cache_file(filename, cache_key, cache_path):
    """
    缓存文件
    :param filename: 要cache的文件名
    :param cache_path: cache保存目录
    :param cache_key: cache唯一key
    """
    #_, ext = os.path.splitext(filename)
    return cp(filename, os.path.join(cache_path, md5(cache_key)))


def get_cache_file(cache_key, cache_path):
    """
    缓存文件
    :param filename: 要cache的文件名
    :param cache_path: cache保存目录
    :param cache_key: cache唯一key
    """
    cache_file = os.path.join(cache_path, md5(cache_key))
    if os.path.exists(cache_file):
        return cache_file
    return None


def full2half(s):
    """字符串全角转半角"""
    res = ""
    for uchar in s:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            res += chr(32)
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            res += chr(inside_code - 65248)
        else:
            res += uchar.replace('。', '.').replace('《', '<').replace('》', '>').replace('「', '[').replace('」', ']')
    return res


def clear_punctuation(s, split=''):
    """清理字符串中的标点符号"""
    s = full2half(s)
    return s.translate(str.maketrans('', split, string.punctuation))


if __name__ == '__main__':
    """函数测试"""

    print(md5('B000000115915'))
    print(get_date(1548124450.6668496))
    print(get_file_rowcount(CUR_PATH + '/utils.py'))
    print(get_path_filecount(CUR_PATH))
    print(get_video_info('/Users/yanjingang/project/data/video/474.mp4'))

    # qrcode
    qrbox, debox, sbox = qrcode_detect(img_file=CUR_PATH+'/data/image/test-qrcode.png', debug_path=CUR_PATH+'/data/tmp/')
    print(qrbox, debox)

    # gui
    '''from pygui import PySimpleGUI as sg
    layout = [
        [sg.Text('filename', size=(100, 1), key='filename')]
    ]
    window = sg.Window('test', return_keyboard_events=True, default_element_size=(30, 2), location=(0, 0), use_default_focus=False).Layout(layout).Finalize()
    window.Close()'''

    # pinyin
    print(get_pinyin('上海'))
    print(get_pinyin('上海', split=' ', tone_marks='marks'))
    print(get_shengmu('上海'))

    # conf
    d = {'master': {'name': 'a', 'nick': '你好', 'faceid': '1'}}
    filename = '/tmp/test.conf'
    format = 'yaml'
    ret = dump_conf(d, filename, format)
    print(load_conf(filename, format))

    # play
    play_sound("on.wav", callback=None)

    # file
    print("get_file_content: {}".format(get_file_content(filename)))
    print("write_temp_file: {}".format(write_temp_file('aaa', '.txt')))
    print("cache_file: {}".format(cache_file(filename, 'kkk', '/tmp/')))
    print("get_cache_file: {}".format(get_cache_file('kkk', '/tmp/')))

    # str
    s = "（字符串）！：「全角」，转《半角》？。"
    print(full2half(s))
    print(clear_punctuation(s))
