# encoding: UTF-8
from __future__ import division, print_function

import os
import math
import torch
from tqdm import tqdm
from collections import OrderedDict
from ptcaffe.utils.logger import logger

from .base_server import BaseServer
from flask import request, jsonify, redirect, url_for
import time
import numpy as np
import threading
from collections import OrderedDict

class ClassificationServer(BaseServer):
    def __init__(self, protofile, weightfile, device):
        super(ClassificationServer, self).__init__(protofile, weightfile, device)

        server_param = self.net.net_info.get('server', OrderedDict())
        classification_param = server_param.get('classification_param', OrderedDict())

        if 'classes_file' in classification_param:
            self.classes = load_classes(classification_param['classes_file'])
        elif 'classes' in classification_param:
            self.classes = classification_param['classes'].split(',')
        else:
            self.classes = None
            logger.warning("classes or classes_file is needed in classification_param")

        self.top_k = int(classification_param.get('top_k', 1))
        assert(self.top_k >= 1)

        self.samples_per_class = [0] * len(self.classes)
        for imgfile,line in self.gt_dict.items():
            gt_id = int(line.split()[1])
            self.samples_per_class[gt_id] += 1

        self.badcases = None
        self.labfiles = None
        self.lab_dict = OrderedDict()

        self.route('/download_badcases',   methods=['GET']        )(self.download_badcases)
        self.route('/download_labels',   methods=['GET']        )(self.download_labels)
       
    def inference(self):
        eval_outputs = self.net.eval_outputs
        if len(eval_outputs) != 1:
            return "Only one output is allowed, the output should from InnerProduct or Softmax"

        if request.method == 'GET':
            imgfile = request.args.get('filename')
            result = self.forward(imgfile) 
            num_classes = result.numel()
            assert(self.top_k <= num_classes)

            browse_mode = int(request.args.get('browse_mode', 0))
            if browse_mode:
                output_html = '<img src="%s" width=%d height=%d></img>' % (imgfile, self.display_width, self.display_height)
            else:
                output_html = '<img src="%s"></img>' % imgfile

            if imgfile in self.gt_dict:
                items  = self.gt_dict[imgfile].split()
                if len(items) > 1:
                    clsid = int(items[1])
                    label = self.classes[clsid] if self.classes else "class%d" % clsid
                    output_html += "<p> gt: %s" % label

            if self.top_k == 1:
                max_val,max_id = result.cpu().max(1)
                max_id = max_id[0]
                max_val = max_val[0]
                max_label = self.classes[max_id] if self.classes else "class%d" % max_id
                output_html = output_html + ' <p> %s : %f' % (max_label, max_val)
            else:
                max_vals, max_ids = result.topk(self.top_k, 1)
                max_vals = max_vals.view(-1).tolist()
                max_ids = max_ids.view(-1).tolist()
                for idx in range(self.top_k):
                    cls_id = max_ids[idx]
                    value  = max_vals[idx]
                    label  = self.classes[cls_id] if self.classes else "class%d" % cls_id
                    output_html = output_html + '<p> %s : %f' % (label, value)

        elif request.method == 'POST':
            buffer = six.BytesIO(request.get_data())
            result = self.forward(buffer) 

            num_classes = result.numel()
            assert(self.top_k <= num_classes)
    
            output_labels = []
            output_probs = []

            if self.top_k == 1:
                max_val,max_id = result.cpu().max(1)
                max_id = max_id[0]
                max_val = max_val[0]
                max_label = self.classes[max_id] if self.classes else "class%d" % max_id
                output_labels.append(max_label)
                output_probs.append(max_val)
            else:
                max_vals, max_ids = result.topk(self.top_k, 1)
                max_vals = max_vals.view(-1).tolist()
                max_ids = max_ids.view(-1).tolist()
                for idx in range(self.top_k):
                    cls_id = max_ids[idx]
                    value  = max_vals[idx]
                    label  = self.classes[cls_id] if self.classes else "class%d" % cls_id
                    output_labels.append(label)
                    output_probs.append(value)

            output_dict = dict()
            output_dict['labels'] = output_labels
            output_dict['probs'] = output_probs
            output_html = jsonify(output_dict)

        return output_html

    def add_badcase(self, result, line):
        imgfile, gt_id = line.split()
        gt_id = int(gt_id)
        gt_prob = result[gt_id]

        max_val, max_id = result.max(0)
        if max_id != gt_id:
            if self.badcases is None:
                self.badcases = []
            self.badcases.append([imgfile, gt_id, gt_prob, max_id, max_val])

    def analysis(self):
        if self.source is None: return "listfile is empty"

        output_html = super(ClassificationServer, self).analysis()

        output_html += '<p><a href="analysis?method=badcase">错误案例</a> | <a href="analysis?method=accuracy">每类准确率</a>'

        method = str(request.args.get('method', 'badcase'))
        if method == 'badcase':
            output_html += self.badcase_result()
        elif method == 'accuracy':
            output_html += self.accuracy_result()

        return output_html

    def download_badcases(self):
        if self.badcases is None: return "No badcase"

        class_id = int(request.args.get('class_id', -1))
        badcases = get_badcases_by_class(self.badcases, class_id)
        output_html = ""
        case_files = []
        for items in badcases:
            output_html += "%s gt:%d pred:%d<br>" % (items[0], items[1], items[3])

        return output_html

    def download_labels(self):
        output_html = ''
        for idx, (key, value) in enumerate(self.lab_dict.items()):
            output_html += "%d: %s %d<br>" % (idx+1, key, value)
        return output_html

    def accuracy_result(self):
        output_html = ""

        if self.all_preds and not self.predicting:
            cases_per_class = [0.0] * len(self.classes)
            acc_per_class = [0.0] * len(self.classes)
            confusion_matrix = np.zeros((len(self.classes), len(self.classes))).astype(np.int32)
            for items in self.badcases:
                gt_id = items[1]
                cases_per_class[gt_id] += 1
                max_id = items[3].numpy()
                confusion_matrix[max_id, gt_id] += 1
            for cls_id in range(len(self.classes)):
                confusion_matrix[cls_id, cls_id] = int(self.samples_per_class[cls_id])
                if self.samples_per_class[cls_id] == 0:
                    acc_per_class[cls_id] = 0.0
                else:
                    acc_per_class[cls_id] = 1.0 - cases_per_class[cls_id]/float(self.samples_per_class[cls_id])
            if not os.path.exists('./plot'):
                os.makedirs('./plot')
            plot_array(self.classes, acc_per_class, 'accuracy per class', "./plot/result_accuracy.png")
            plot_array(self.classes, self.samples_per_class, 'samples per class', "./plot/result_samples.png")
            if len(self.classes) < 20:
                plot_confusion_matrix_num(self.classes, confusion_matrix, 'confusion matrix', "./plot/confusion_matrix.png")
            else:
                plot_confusion_matrix(self.classes, confusion_matrix, 'confusion matrix', "./plot/confusion_matrix.png")
            output_html += '<p><div><img src="./plot/result_accuracy.png"></img><p>每类准确率</div.'
            output_html += '<p><div><img src="./plot/result_samples.png"></img><p>每类样本数</div.'
            output_html += '<p><div><img src="./plot/confusion_matrix.png"></img><p>混淆矩阵</div>'
            output_html += '<p>平均准确率%.5f' % np.mean(acc_per_class)
        return output_html

    def badcase_result(self):
        class_id = int(request.args.get('class_id', -1))
        method = str(request.args.get('method', 'badcase'))

        while self.badcases is None or len(self.badcases) == 0:
            time.sleep(1)

        badcases = get_badcases_by_class(self.badcases, class_id)

        processed_percent = int(self.predicted_samples // len(self.imgfiles) *100)
        avg_accuracy = 1.0 - len(self.badcases) / float(self.predicted_samples)
        table_html = '分析进度%d%% (%d/%d) 发现错误案例 %d 准确率 %.5f ' % (processed_percent, self.predicted_samples, len(self.imgfiles), len(self.badcases), avg_accuracy)
        if class_id != -1:
            class_accuracy = 1.0 - len(badcases) / float(self.samples_per_class[class_id])
            table_html += ' 类别%d准确率 %.5f (%d/%d)' % (class_id, class_accuracy, len(badcases), self.samples_per_class[class_id])
        table_html += '<p><table>'

        display_cols = self.display_cols
        display_rows = self.display_rows
        
        imgs_per_page = display_cols * display_rows
        num_imgs = len(badcases)

        num_pages = int(math.ceil(num_imgs / imgs_per_page))
        num_pages = max(num_pages, 1)

        page_id = int(request.args.get('page_id', 1))
        page_id = min(max(page_id, 1), num_pages)

        prev_page_url  = "analysis?method=%s&page_id=%d&class_id=%d" % (method, max(page_id -1, 1), class_id)
        next_page_url  = "analysis?method=%s&page_id=%d&class_id=%d" % (method, min(page_id +1, num_pages), class_id)
        first_page_url = "analysis?method=%s&page_id=1&class_id=%d" % (method, class_id)
        last_page_url  = "analysis?method=%s&page_id=%d&class_id=%d" % (method, num_pages, class_id)
        print('prev_page_url', prev_page_url)

        page_change_html = '<p><a href="%s">上一页</a> | <a href="%s">下一页</a> | <a href="%s">第一页</a> | <a href="%s">最后一页</a> | <a href="download_badcases?class_id=%d">下载</a>' % (prev_page_url, next_page_url, first_page_url, last_page_url, class_id)


        if len(self.classes) > 20:
            if class_id == -1:
                page_change_html += '<form method=get action=analysis><input type="text" name="class_id" placeholder="选择类别"><input type=submit value="提交"></form>'
            else:
                page_change_html += '<form method=get action=analysis><input type="text" name="class_id" placeholder="%d"><input type=submit value="提交"></form>' % class_id
        else:
            page_change_html += '<form method=get action=analysis><select name="class_id" style="width:100px">'
            if class_id == -1:
                page_change_html += '<option value="-1" selected = "selected" >all</option>'
            else:
                page_change_html += '<option value="-1">all</option>'
            for idx,cls in enumerate(self.classes):
                if class_id == idx:
                    page_change_html += '<option value="%d" selected = "selected">%s</option>' % (idx, cls)
                else:
                    page_change_html += '<option value="%d">%s</option>' % (idx, cls)
            page_change_html += '</select><input type=submit value="提交"></form>'

        for idx in range(imgs_per_page):
            img_id = (page_id-1) * imgs_per_page + idx
            if img_id >= num_imgs: break

            imgfile, gt_id, gt_prob, pred_id, pred_prob = badcases[img_id]
            if idx % self.display_cols == 0:
                table_html += "<tr>"
            pred_label = self.classes[pred_id]
            gt_label = self.classes[gt_id]
            table_html += '<td><div><img src="%s" width=%d height=%d></img><p>gt: %s %.5f<p>pred: %s %.5f</div></td>' % (imgfile, self.display_width, self.display_height, gt_label, gt_prob, pred_label, pred_prob)

        table_html += "</table>"

        output_html = '''
            %s<p>
            <fieldset>
            <legend>错误案例</legend>
            %s
            </fieldset>
        ''' % (page_change_html, table_html)

        return output_html

    def setting(self):
        output_html = super(ClassificationServer, self).setting()
        if request.method == 'GET':
            pass
        classification_setting_html = '''
        <fieldset>
        <legend>分类设置</legend>
        <form method=get enctype=multipart/form-data action="setting">
              <label style="width:50px">类别</label> &nbsp;&nbsp:
              <input type="text" name="classes" style="width:500px" placeholder="%s"><p>
              <input type=file name=file style="width:300px">
              <p>
              <input type=submit style="width:100px" value="提交">
        </form>
        </fieldset>
        ''' % ','.join(self.classes)
        return output_html + classification_setting_html

    def labeling(self): 
        if request.method == 'POST':
            disp_id = int(request.form.get('disp_id'))
            num_files = len(self.labfiles)
            disp_id = min(max(disp_id, 1), num_files)
            img_id = disp_id - 1

            choose_value = int(request.form.get('choose_value'))
            imgfile = self.labfiles[img_id]
            self.lab_dict[imgfile] = choose_value
            return redirect('labeling?disp_id=%d' % (disp_id+1))

        if self.source is None: return "没有标注数据"
        # produce labfiles
        if self.labfiles is None:
            if len(self.gt_dict[self.imgfiles[0]].split()) == 1:
                self.labfiles = self.imgfiles
                for imgfile in self.imgfiles:
                    self.lab_dict[imgfile] = int(self.gt_dict[imgfile].split()[1])
            elif self.badcases:
                self.labfiles = []
                for badcase in self.badcases:
                    imgfile = badcase[0]
                    self.labfiles.append(imgfile)
                    if imgfile not in self.lab_dict: 
                        self.lab_dict[imgfile] = badcase[1]

            else:
                if self.all_preds is None:
                    if not self.predicting:
                        threading.Thread(target=self.predict_all).start()
                    return '生成Badcases中 ... <p><progress value="%d" max="%d" style="width:500px">' % (self.predicted_samples, len(self.imgfiles))
                else:
                    return "请先生成badcases"
        elif self.badcases and len(self.badcases) != len(self.labfiles):
            self.labfiles = []
            for badcase in self.badcases:
                imgfile = badcase[0]
                self.labfiles.append(imgfile)
                if imgfile not in self.lab_dict: 
                    self.lab_dict[imgfile] = badcase[1]

        assert(self.labfiles is not None)

        disp_id = int(request.args.get('disp_id', 1))
        num_files = len(self.labfiles)
        disp_id = min(max(disp_id, 1), num_files)
        output_html = '''
            <!doctype html> <head><title>PTCaffe Demo</title>
            <script>
            function save_only() {
                alert("save_only")
            }
            function save_and_next() {
                window.open("?disp_id=%d","_self")
            }
            function getPar(par){
                //获取当前URL
                var local_url = document.location.href; 
                //获取要取得的get参数位置
                var get = local_url.indexOf(par +"=");
                if(get == -1){
                    return false;   
                }   
                //截取字符串
                var get_par = local_url.slice(par.length + get + 1);    
                //判断截取后的字符串是否还有其他get参数
                var nextPar = get_par.indexOf("&");
                if(nextPar != -1){
                    get_par = get_par.slice(0, nextPar);
                }
                return get_par;
            }
            function httpPost(URL, PARAMS) {
                var temp = document.createElement("form");
                temp.action = URL;
                temp.method = "post";
                temp.style.display = "none";
            
                for (var x in PARAMS) {
                    var opt = document.createElement("textarea");
                    opt.name = x;
                    opt.value = PARAMS[x];
                    temp.appendChild(opt);
                }
            
                document.body.appendChild(temp);
                temp.submit();
            }
            function choose_and_next(a) {
                disp_id = getPar('disp_id');
                if(disp_id == false) disp_id = 1;
                choose_value = a.value;
                var params = new Array();
                params['disp_id'] = disp_id;
                params['choose_value'] = choose_value;
                httpPost("labeling", params)
            }
            </script></head>
            %s 
            <p> <hr>
        ''' % (min(disp_id+1, num_files), self.nav_html)

        prev_img_url  = 'labeling?disp_id=%d' % max(disp_id-1, 1)
        next_img_url  = 'labeling?disp_id=%d' % min(disp_id+1, num_files)
        first_img_url = 'labeling?disp_id=1'
        last_img_url  = 'labeling?disp_id=%d' % num_files

        output_html += '<a href="%s">上一张</a> | <a href="%s">下一张</a> | <a href="%s">第一张</a> | <a href="%s">最后一张</a> | <form method=get action=labeling style="margin:0px;display:inline;">第<input type="text" name="disp_id" style="width:50px" placeholder="%d">张 <input type=submit value="跳转"></form> 总共%d张 | <a href="download_labels">下载标注</a>' % (prev_img_url, next_img_url, first_img_url, last_img_url, disp_id, num_files)
        
        img_id = disp_id - 1
        imgfile = self.labfiles[img_id]
        output_html += '<p><img src="%s" width=%d height=%d></img>' % (imgfile, self.display_width, self.display_height)
        
        # predict
        top_k = 5
        result = self.forward(imgfile).detach().cpu()
        max_vals, max_ids = result.topk(top_k, 1)

        output_html += '<p><fieldset style="width:500px"> <legend>选择类别</legend><div>'
        for idx in range(top_k):
            cls_id = int(max_ids[0][idx])
            label = self.classes[cls_id] if self.classes else str(cls_id)
            output_html += '<button type="submit" name="choose_label" value="%d" style="width:200px;height:30px" onclick="choose_and_next(this)">[%d] %s</button><p>' % (cls_id, cls_id, label)
        output_html += '</div></fieldset>'

        return output_html
 
def load_classes(filename):
    outputs = []
    with open(filename, 'r') as fp:
        lines = fp.readlines()
    for line in lines:
        label = line.strip()
        if label != "":
            outputs.append(label)
    return outputs


def get_badcases_by_class(badcases, class_id):
    if class_id == -1: return badcases
    subcases = []
    for items in badcases:
        if items[1]==class_id:
            subcases.append(items)
    return subcases

def plot_array(keys, values, title, filename):
    import matplotlib 
    matplotlib.use('Agg') #should before plt
    import matplotlib.pyplot as plt
    plt.figure()
    if len(keys) < 20:
        plt.bar(keys, values)
    else:
        plt.bar(keys, values)
        plt.xticks([])
    plt.title(title)
    plt.savefig(filename)
    plt.close()

# from matplotlib.org
def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Arguments:
        data       : A 2D numpy array of shape (N,M)
        row_labels : A list or array of length N with the labels
                     for the rows
        col_labels : A list or array of length M with the labels
                     for the columns
    Optional arguments:
        ax         : A matplotlib.axes.Axes instance to which the heatmap
                     is plotted. If not provided, use current axes or
                     create a new one.
        cbar_kw    : A dictionary with arguments to
                     :meth:`matplotlib.Figure.colorbar`.
        cbarlabel  : The label for the colorbar
    All other arguments are directly passed on to the imshow call.
    """
    import matplotlib 
    matplotlib.use('Agg') #should before plt
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    ax.set_xlabel('Precision')
    ax.xaxis.set_label_position('top') 
    ax.set_ylabel('Recall')

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Arguments:
        im         : The AxesImage to be labeled.
    Optional arguments:
        data       : Data used to annotate. If None, the image's data is used.
        valfmt     : The format of the annotations inside the heatmap.
                     This should either use the string format method, e.g.
                     "$ {x:.2f}", or be a :class:`matplotlib.ticker.Formatter`.
        textcolors : A list or array of two color specifications. The first is
                     used for values below a threshold, the second for those
                     above.
        threshold  : Value in data units according to which the colors from
                     textcolors are applied. If None (the default) uses the
                     middle of the colormap as separation.

    Further arguments are passed on to the created text labels.
    """
    import matplotlib 
    matplotlib.use('Agg') #should before plt
    import matplotlib.pyplot as plt
    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[im.norm(data[i, j]) > threshold])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

def plot_confusion_matrix_num(labels, confusion_matrix, title, filename):
    import matplotlib 
    matplotlib.use('Agg') #should before plt
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator

    matrix = confusion_matrix.astype(np.float)
    presicion = np.diag(matrix)/ matrix.sum(1)
    recall = np.diag(matrix)/ matrix.sum(0)
    x_label = ['{:s} {:.1f}'.format(labels[i],presicion[i]*100) for i in range(len(labels))]
    y_label = ['{:s} {:.1f}'.format(labels[i],recall[i]*100) for i in range(len(labels))]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    im, cbar = heatmap(confusion_matrix, x_label, y_label, ax=ax,
                       cmap="YlGn", cbarlabel='Count')
    texts = annotate_heatmap(im, valfmt="{x:d}")
    fig.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_confusion_matrix(labels, confusion_matrix, title, filename):
    import matplotlib 
    matplotlib.use('Agg') #should before plt
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator

    plt.imshow(confusion_matrix)
    plt.title(title)
    plt.colorbar()
    plt.xticks([])
    plt.yticks([])
    plt.savefig(filename)
    plt.close()

