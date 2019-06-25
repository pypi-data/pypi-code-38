# encoding: UTF-8
from __future__ import print_function, division

import os
import six
import math
import torch
import PIL.Image
from ptcaffe.caffenet import CaffeNet
from ptcaffe.transforms import create_transform
from ptcaffe.utils.logger import logger
from collections import OrderedDict

import torchvision.transforms as T

from tqdm import tqdm
import threading
import requests
from flask import Flask, request, jsonify, redirect, url_for, make_response

if six.PY2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

class BaseServer(Flask):
    def __init__(self, protofile, weightfile, device):
        self.protofile = protofile
        self.device = device

        net = CaffeNet(protofile, phase='TEST')
        if weightfile is not None:
            net.load_model(weightfile)
        net.eval()
     
        # GPU
        if device:
            if device.find(',') == -1:
                logger.info('single gpu device %s' % device)
                device_id = int(device)
                net.cuda(device_id)
                net.broadcast_device_ids([device_id])
            else:
                device_ids = device.split(',')
                logger.info('multi gpu devices %s' % device)
                device_ids = [int(i) for i in device_ids]
                net = ParallelCaffeNet(net.cuda(device_ids[0]), device_ids=device_ids)
    
        self.net = net

        server_param = net.net_info.get('server', OrderedDict())
        self.port = int(server_param.get('port', 8080))
        self.name = server_param.get('name', "")

        self.source = server_param.get('source')
        self.display_cols = 3
        self.display_rows = 3
        self.display_width = 200
        self.display_height = 200
        self.batch_size = 100

        if self.source is not None:
            if self.source.find('.txt') > 0 or self.source.find('.list') >= 0:
                lines = open(self.source, 'r').readlines()
                self.imgfiles = [line.split()[0] for line in lines] 
                self.gt_dict = dict()
                for imgfile, line in zip(self.imgfiles, lines):
                    self.gt_dict[imgfile] = line

        preprocess_param = server_param.get('preprocess_param', None)

        if preprocess_param is None:
            input_shape = self.net.get_input_shapes()
            logger.info('input_shape: %s' % str(input_shape))
            preprocess_param = OrderedDict()
            if input_shape[1] == 1:
                preprocess_param['pil_loader'] = {'color_mode': "gray"}
            elif input_shape[1] == 3:
                preprocess_param['pil_loader'] = {'color_mode': "rgb"}
            preprocess_param['pil_resize'] = {'size': [str(input_shape[2]), str(input_shape[3])]}
            preprocess_param['pil2tensor'] = {}
            preprocess_param['tensor_unsqueeze'] = {'dim': '0'}
        logger.info('preprocess_param: %s' % str(preprocess_param))

        self.preprocess = create_transform(preprocess_param)

        # for predict_all
        self.all_preds = None
        self.predicting = False
        self.predicted_samples = 0

        super(BaseServer, self).__init__('ptcaffe server', static_folder='', static_url_path='')
	
        self.route('/',          methods=['GET']        )(self.homepage)
        self.route('/upload',    methods=['GET', 'POST'])(self.upload)
        self.route('/inference', methods=['GET', 'POST'])(self.inference)
        self.route('/browse',    methods=['GET']        )(self.browse)
        self.route('/analysis',  methods=['GET']        )(self.analysis)
        self.route('/labeling',  methods=['GET', 'POST'])(self.labeling)
        self.route('/graph',     methods=['GET']        )(self.graph)
        self.route('/convert',   methods=['GET']        )(self.convert)
        self.route('/setting',   methods=['GET']        )(self.setting)


    @property
    def nav_html(self):
        return '<a href="/">首页</a> | <a href="upload">上传文件</a> | <a href="browse">数据浏览</a> | <a href="analysis">结果分析</a> | <a href="labeling">数据标注</a> | <a href="graph">网络结构</a> | <a href="convert">模型转换</a> | <a href="setting">设置</a>'

    def homepage(self):
        output_html = '''
            <!doctype html> <title>PTCaffe Demo</title> 
            %s <p> <hr>
            <p>
        ''' % self.nav_html
        return output_html

    def forward(self, file_or_buffer):
        data = self.preprocess(file_or_buffer)

        if self.device:
            data = data.cuda()

        with torch.no_grad():
            result = self.net(data) 
        return result

    def browse(self):
        if self.source is None: return "listfile is empty"
        display_cols = self.display_cols
        display_rows = self.display_rows
        imgs_per_page = display_cols * display_rows
        num_imgs = len(self.imgfiles)
        num_pages = int(math.ceil(num_imgs / imgs_per_page))
        page_id = int(request.args.get('page_id', 1))
        page_id = min(max(page_id, 1), num_pages)
        view_type = int(request.args.get('view', 1))
        batch_predict = int(request.args.get('batch_predict', 0))

        prev_page_url = "browse?page_id=%d&view=%d" % (max(page_id -1, 1), view_type)
        next_page_url = "browse?page_id=%d&view=%d" % (min(page_id +1, num_pages), view_type)
        first_page_url = "browse?page_id=1&view=%d" % view_type
        last_page_url = "browse?page_id=%d&view=%d" % (num_pages,view_type)
        change_view_url = "browse?page_id=%d&view=%d" % (page_id, (view_type+1)%2)
        batch_predict_url = "browse?page_id=%d&view=%d&batch_predict=1" % (page_id, view_type)

        page_change_html = '<a href="%s">上一页</a> | <a href="%s">下一页</a> | <a href="%s">第一页</a> | <a href="%s">最后一页</a> | <a href="%s">切换视图</a> | <a href="%s">批量预测</a>' % (prev_page_url, next_page_url, first_page_url,last_page_url, change_view_url, batch_predict_url)

        output_html = self.nav_html + "<p><hr>" + page_change_html + "<p>"
        if view_type == 0: #'list'
            for idx in range(imgs_per_page):
                img_id = (page_id-1) * imgs_per_page + idx
                if img_id >= num_imgs: break
                imgfile = self.imgfiles[img_id]
                if batch_predict == 0:
                    output_html += '<a href="inference?filename=%s"><img src="%s"></img></a><p>' % (imgfile, imgfile)
                elif batch_predict == 1:
                    result_html = urlopen("http://localhost:%s/inference?filename=%s&browse_mode=0" % (self.port, imgfile)).read()
                    output_html += '<p> %s' % result_html
        elif view_type == 1: #'grid'
            output_html += "<table>"
            for idx in range(imgs_per_page):
                row = idx // display_cols
                col = idx % display_cols
                img_id = (page_id-1) * imgs_per_page + idx
                if img_id >= num_imgs: break
                imgfile = self.imgfiles[img_id]

                if col == 0:
                    output_html += "<tr>"
                if batch_predict == 0:
                    output_html += '<td><a href="inference?filename=%s"><img src="%s" width=%d height=%d></img></a></td>' % (imgfile, imgfile, self.display_width, self.display_height)
                elif batch_predict == 1:
                    #result = requests.post(url="http://10.60.242.133:8080/inference", data=open(imgfile).read(), headers={'Content-Type': 'application/octet-stream'})
                    #logger.info('result: %s' % str(result))
                    result_html = urlopen("http://localhost:%d/inference?filename=%s&browse_mode=1" % (self.port, imgfile)).read()
                    output_html += '<td><div>%s</div></td>' % result_html
            output_html += "</table>"
        return output_html

    def inference(self):
        eval_outputs = self.net.eval_outputs
        if request.method == 'GET':
            imgfile = request.args.get('filename')
            result = self.forward(imgfile) 

            if len(eval_outputs) == 1:
                output_html = "%s: %s" % (eval_outputs[0], result.cpu().tolist())
            elif len(eval_outputs) > 1:
                output_html = ""
                for idx,name in enumerate(eval_outputs):
                    output_html += '%s: %s <p>' % (name, result[idx].cpu().tolist())
            output_html = ' <img src="%s"></img> <p> %s' % (imgfile, output_html)
            return output_html

        elif request.method == 'POST':
            buffer = six.BytesIO(request.get_data())
            result = self.forward(buffer) 

            if len(eval_outputs) == 1: result = [result]
    
            output = dict()
            for idx, name in enumerate(eval_outputs):
                output[name] = result[idx].cpu().tolist()
            output_json = jsonify(output)
            return output_json

    def graph(self):
        try:
            from ptcaffe.tools.prototxt2graph import prototxt2graph_advanced

            dotfile = "./graph/graph.dot"
            outfile = "./graph/graph.png"
            if not os.path.exists('./graph'):
                os.makedirs('./graph')
            if not os.path.exists(outfile):
                prototxt2graph_advanced(self.protofile, dotfile)
                os.system("dot -Tpng -o %s %s" % (outfile, dotfile))

            output_html = '''
            <!doctype html> <title>PTCaffe Demo</title> 
            %s <p> <hr>
            <p> <a href="http://ethereon.github.io/netscope/#/editor">netscope</a> | <a href="https://dgschwend.github.io/netscope/quickstart.html">dgschwend</a>
            <p> <img src="%s"></img>
            ''' % (self.nav_html, outfile)
            return output_html
        except Exception as e:
            return str(e)
            #return str(self.net.net_info)

    def upload(self):
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                logger.warning('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                logger.warning('No selected file')
                return redirect(request.url)
            if file:
                if not os.path.exists('./uploads'):
                    os.makedirs('./uploads')

                if allowed_file(file.filename):
                    savename = './uploads/%s' % file.filename
                    file.save(savename)
                    logger.info('Save file: %s' % savename)
                    return redirect(url_for('inference', filename="uploads/"+file.filename))
                else:
                    logger.warning('Invalid file: %s' % file.filename)

        output_html = '''
            <!doctype html> <title>PTCaffe Demo</title> 
            %s <p> <hr>
            <p>
            <fieldset>
            <legend>%s</legend>
            <form method=post enctype=multipart/form-data>
              <input type=file name=file style="width:300px">
              <input type=submit value="Upload">
            </form>
            </fieldset>
            '''
        return output_html % (self.nav_html, self.name)

    def predict_all(self):
        self.predicting = True
        self.all_preds = [None] * len(self.imgfiles)

        cache_datas = []
        batch_size = self.batch_size
        for idx, imgfile in enumerate(tqdm(self.imgfiles)):
            data = self.preprocess(imgfile)
            if self.device:
                data = data.cuda()
            cache_datas.append(data)

            if (idx+1) % batch_size == 0:
                batch_data = torch.cat(cache_datas, dim=0)
                with torch.no_grad():
                    result = self.net(batch_data).detach().cpu()
                for batch_id in range(batch_size):
                    self.all_preds.append(result[batch_id])
                    _imgfile = self.imgfiles[idx+1-batch_size + batch_id]
                    if hasattr(self, 'add_badcase'):
                        self.add_badcase(result[batch_id], self.gt_dict[_imgfile])

                del cache_datas
                cache_datas = []
            self.predicted_samples = idx + 1
        self.predicting = False

    def analysis(self):
        if self.source is None: return "listfile is empty"

        if self.all_preds is None:
            if not self.predicting:
                threading.Thread(target=self.predict_all).start()
                #self.predict_all()

        output_html = '''
            <!doctype html> <title>PTCaffe Demo</title> 
            %s 
            <p> <hr>
        ''' % self.nav_html
        if self.predicting:
            output_html += '<progress value="%d" max="%d" style="width:300px"></progress><br>' % (self.predicted_samples, len(self.imgfiles))
        return output_html

    def labeling(self):
        output_html = '''
            <!doctype html> <title>PTCaffe Demo</title> 
            %s 
            <p> <hr>
        ''' % self.nav_html
        disp_id = int(request.args.get('disp_id', 1))
        num_imgs = len(self.imgfiles)
        disp_id = min(max(disp_id, 1), num_imgs)

        prev_img_url = 'labeling?disp_id=%d' % max(disp_id-1, 1)
        next_img_url = 'labeling?disp_id=%d' % min(disp_id+1, num_imgs)
        first_img_url = 'labeling?disp_id=1'
        last_img_url = 'labeling?disp_id=%d' % num_imgs

        output_html += '<a href="%s">上一张</a> | <a href="%s">下一张</a> | <a href="%s">第一张</a> | <a href="%s">最后一张</a> | <form method=get action=labeling style="margin:0px;display:inline;">第<input type="text" name="disp_id" style="width:50px" placeholder="%d">张 <input type=submit value="跳转"></form>' % (prev_img_url, next_img_url, first_img_url, last_img_url, disp_id)
        

        img_id = disp_id - 1
        imgfile = self.imgfiles[img_id]
        output_html += '<p><img src="%s"></img>' % imgfile

        return output_html

    def convert(self):
        output_html = '''
            <!doctype html> <title>PTCaffe Demo</title> 
            %s <p> <hr>
            <p>
            <fieldset>
            <legend>ptcaffe2caffe</legend>
            <form method=get enctype=multipart/form-data action="setting">
              <label style="width:120px">input_protofile</label> &nbsp;&nbsp:
              <input type=file name="input_protofile" style="width:300px" value="input_protofile" alt="input_protofile">
              <p>
              <label style="width:120px">input_weightfile</label> &nbsp;&nbsp:
              <input type=file name="input_weightfile" style="width:300px" value="input_weightfile" alt="input_weightfile">
              <p>
              <label style="width:120px">output_protofile</label> &nbsp;&nbsp:
              <input type="text" name="output_protofile" style="width:200px">
              <p>
              <label style="width:120px">output_weightfile</label> &nbsp;&nbsp:
              <input type="text" name="output_weightfile" style="width:200px">
              <p>
              <input type=submit style="width:100px" value="提交">
            </form>
            </fieldset>
            '''

        return output_html % self.nav_html

    def setting(self):
        if request.method == 'GET':
            #import pdb; pdb.set_trace()
            display_rows = request.args.get('display_rows')
            if display_rows: self.display_rows = int(display_rows)
            display_cols = request.args.get('display_cols')
            if display_cols: self.display_cols = int(display_cols)
            display_width = request.args.get('display_width')
            if display_width: self.display_width = int(display_width)
            display_height = request.args.get('display_height')
            if display_height: self.display_height = int(display_height)

        output_html = '''
            <!doctype html> <title>PTCaffe Demo</title> 
            %s <p> <hr>
            <p>
            <fieldset>
            <legend>显示设置</legend>
            <form method=get enctype=multipart/form-data action="setting">
              <label style="width:50px">行数</label> &nbsp;&nbsp:
              <input type="text" name="display_rows" style="width:100px" placeholder="%d">
              <p>
              <label style="width:50px">列数</label> &nbsp;&nbsp:
              <input type="text" name="display_cols" style="width:100px" placeholder="%d">
              <p>
              <label style="width:50px">宽度</label> &nbsp;&nbsp:
              <input type="text" name="display_width" style="width:100px" placeholder="%d">
              <p>
              <label style="width:50px">高度</label> &nbsp;&nbsp:
              <input type="text" name="display_height" style="width:100px" placeholder="%d">
              <p>
              <input type=submit style="width:100px" value="提交">
            </form>
            </fieldset>
            '''
        return output_html % (self.nav_html, self.display_rows, self.display_cols, self.display_width, self.display_height)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(['txt', 'png', 'jpg', 'jpeg', 'bmp'])
