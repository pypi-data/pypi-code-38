# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import defaultdict
import os
import pandas
import sys
import time
import re


reload(sys)
sys.setdefaultencoding('utf8')

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Nanopore测序数据统计分析报告</title>
</head>
<body>
    {body}
</body>
</html>
'''

def buildDOC(body):
    """
    :param body: body of TEMPLATE
    """
    try:
        html = TEMPLATE.format(
            body=body
        )  # 向模板中填充数据
        return html
    except Exception as err:
        raise err


def write_to_file(html, file):
    """
    write html to file
    """
    with open(file, 'w') as f:
        f.write(html)


def statistics(outdir, prefix=None):
    stat_raw = defaultdict(lambda: defaultdict(lambda: []))
    stat_filtered = defaultdict(lambda: defaultdict(lambda: []))
    len_dist = []

    if os.path.isdir(os.path.join(outdir, 'quality_control')):
        for item in os.listdir(os.path.join(outdir, 'quality_control')):
            if item.endswith('_QCstat.out') and not item.startswith("filtered_"):
                prefix = item.replace('_QCstat.out', '')
                if prefix == 'none':
                    continue
                with open(os.path.join(outdir, 'quality_control', item)) as f:
                    for line in f:
                        if line.startswith('# Fastq stats for'):
                            read_len = int((line.strip().split('reads >= '))[-1].replace('bp', ''))
                            len_dist.append(read_len)
                            for i in range(10):
                                line = next(f)
                                tmp = line.strip().split(': ')[-1]
                                if line.startswith('%') or line.startswith('meanLen'):
                                    tmp = round(float(tmp), 2)
                                stat_raw[prefix][read_len].append(tmp)
            elif item.endswith('_QCstat.out') and item.startswith("filtered_"):
                prefix = item.replace('_QCstat.out', '').replace('filtered_', '')
                if prefix == 'none':
                    continue
                with open(os.path.join(outdir, 'quality_control', item)) as f:
                    for line in f:
                        if line.startswith('# Fastq stats for'):
                            read_len = int((line.strip().split('reads >= '))[-1].replace('bp', ''))
                            len_dist.append(read_len)
                            for i in range(10):
                                line = next(f)
                                tmp = line.strip().split(': ')[-1]
                                if line.startswith('%') or line.startswith('meanLen'):
                                    tmp = round(float(tmp), 2)
                                stat_filtered[prefix][read_len].append(tmp)
    elif os.path.exists(os.path.join(outdir, 'QCstat.out')) and os.path.exists(os.path.join(outdir, 'filtered_QCstat.out')):
        if prefix is None:
            prefix = 'SAMPLE'

        with open(os.path.join(outdir, 'QCstat.out')) as f:
            for line in f:
                if line.startswith('# Fastq stats for'):
                    read_len = int((line.strip().split('reads >= '))[-1].replace('bp', ''))
                    len_dist.append(read_len)
                    for i in range(10):
                        line = next(f)
                        tmp = line.strip().split(': ')[-1]
                        if line.startswith('%') or line.startswith('meanLen'):
                            tmp = round(float(tmp), 2)
                        stat_raw[prefix][read_len].append(tmp)

        with open(os.path.join(outdir, 'filtered_QCstat.out')) as f:
            for line in f:
                if line.startswith('# Fastq stats for'):
                    read_len = int((line.strip().split('reads >= '))[-1].replace('bp', ''))
                    len_dist.append(read_len)
                    for i in range(10):
                        line = next(f)
                        tmp = line.strip().split(': ')[-1]
                        if line.startswith('%') or line.startswith('meanLen'):
                            tmp = round(float(tmp), 2)
                        stat_filtered[prefix][read_len].append(tmp)
    else:
        print('Not found "quality_control" dir or stat file: "QCstat.out" and "filtered_QCstat.out" in dir {}.'.format(outdir))
        sys.exit(-1)

    with open(os.path.join(outdir, 'raw_reads_stat.xls'), 'w') as f:

        f.write('sample\treads >=\tnumReads\t%totalNumReads\tnumBasepairs\t%totalBasepairs\tmeanLen\tmedianLen\tminLen\tmaxLen\tN50\tL50\n')

        for key in sorted(stat_raw.keys()):
            for subkey in sorted(set(len_dist)):
                if subkey in stat_raw[key].keys():
                    f.write('{}\t>={}kb\t{}\n'.format(key, round(subkey/1000, 2), '\t'.join(map(str, stat_raw[key][subkey]))))
                else:
                    f.write('{}\t>={}kb\t{}\n'.format(key, round(subkey/1000, 2), '\t'.join(['0'] * 10)))

    with open(os.path.join(outdir, 'filtered_reads_stat.xls'), 'w') as f:
        f.write('sample\treads >=\tnumReads\t%totalNumReads\tnumBasepairs\t%totalBasepairs\tmeanLen\tmedianLen\tminLen\tmaxLen\tN50\tL50\n')
        for key in sorted(stat_filtered.keys()):
            for subkey in sorted(set(len_dist)):
                if subkey in stat_filtered[key].keys():
                    f.write('{}\t>={}kb\t{}\n'.format(key, round(subkey/1000, 2), '\t'.join(map(str, stat_filtered[key][subkey]))))
                else:
                    f.write('{}\t>={}kb\t{}\n'.format(key, round(subkey/1000, 2), '\t'.join(['0'] * 10)))


def read_table(file):
    """
    convert to html format table
    """
    data = {}
    # df = pd.DataFrame(data)
    with open(file, 'r') as f:
        header = f.readline().replace('\n', '').split('\t')
        for item in header:
            data[item] = []
        for line in f.readlines():
            line = line.replace('\n', '')
            temp = line.split('\t')
            for i in range(len(temp)):
                data[header[i]].append(temp[i])
    return data, header


def to_html(raw_stat, filtered_stat, min_quality=7, min_len=2000, max_len=None, png=None):
    localtime = time.strftime("%Y-%m-%d", time.localtime())
    body = '<div style="text-align: center;vertical-align: middle;">'
    if max_len is not None:
        start = '2）过滤低质量read：(a) 剔除平均质量值Q小于{}的read；(b) 剔除长度小于{} bp或长度大于{} bp的read。'.format(min_quality, min_len, max_len)
    else:
        start = '2）过滤低质量read：(a) 剔除平均质量值Q小于{}的read；(b) 剔除长度小于{} bp的read。'.format(min_quality, min_len)

    body += ('<img src="./logo.jpg" height="8%" width="8%" style="float:left;"><h4 style="float:right;">{}</h4>\n'
        '<h1 align="center">Nanopore测序数据基本统计分析报告</h1>\n'
        '<hr style="FILTER: alpha(opacity=100,finishopacity=0,style=2)" width="100%" color=#A2CD5A SIZE=10>\n'
        '<h2>===== 质控分析简介 ====</h2>\n'
        '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="80%" >\n'
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<p align="left" style="font-size:120%">\n'
        '<br />{}本流程针对Nanopore原始下机数据进行处理，支持fast5或fastq两种格式。基本步骤包括：'
        '<br />{}1）去接头，拆分barcode标签（可选）：利用Qcat软件去除接头序列，同时利用Guppy对不同样本进行拆分，得到各样本的测序数据(如果测序过程中添加了barcode标签)。\n'
        '<br />{}{}\n'
        '<br />{}3）统计基本信息：包括原始测序数据和过滤后的测序数据两部分，具体统计信息如下。</p>\n'
        '<h2>===== 原始测序数据 ====</h2>\n'
        '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="80%" >\n'
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<h3>1. 基本信息统计表</h3>\n'
        '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="50%">\n'
        '<hr style="border:1px dashed #A2CD5A" width="50%" color=#A2CD5A SIZE=3>\n'
        ).format(localtime, '&nbsp' * 30, '&nbsp' * 30, '&nbsp' * 30, '&nbsp' * 30, start, '&nbsp' * 30)
    raw_data, raw_header = read_table(raw_stat)
    raw_df = pandas.DataFrame(raw_data, columns=raw_header)
    # body += raw_df.to_html(index=False)
    tmp = raw_df.to_html(index=False)
    tmp = re.sub('<table border="1" class="dataframe">', '<table border="1" width="80%" class="dataframe" style="text-align: right; margin:auto"><caption>表1：原始测序数据基本信息统计表</caption>', tmp)
    body += tmp

    body += ('<h3>2. Reads长度-质量值分布图</h3>\n'
            '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="50%">\n'
            '<hr style="border:1px dashed #A2CD5A" width="50%" color=#A2CD5A SIZE=3>\n')
    # body = '<style> img {width: 100px;} </style>\n'

    if os.path.isdir(os.path.join(os.path.dirname(raw_stat), 'quality_control')):
        qc_path = os.path.join(os.path.dirname(raw_stat), 'quality_control')
        for item in os.listdir(qc_path):
            if item.endswith('.png') and not item.startswith('filtered_'):
                if item.startswith('none_') or item.startswith('filtered_none_'):
                    continue
                # body += '<img src=\"{}\">\n'.format(os.path.join(qc_path, item))
                body += '<img src=\"./{}\" height="40%" width="40%"><br />\n'.format(os.path.join('quality_control', item))
    else:
        qc_path = os.path.dirname(raw_stat)
        for item in os.listdir(qc_path):
            if item.endswith('.png') and not item.startswith('filtered_'):
                if item.startswith('none_') or item.startswith('filtered_none_'):
                    continue
                # body += '<img src=\"{}\">\n'.format(os.path.join(qc_path, item))
                body += '<img src=\"./{}\" height="40%" width="40%">\n'.format(item)


    body += (
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="80%" >\n'
        '<h2>===== 过滤后测序数据 ====</h2>\n'
        '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="80%" >\n'
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<hr style="border:1px dashed #A2CD5A" width="80%" color=#A2CD5A SIZE=3>\n'
        '<h3>1. 基本信息统计表</h3>\n'
        '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="50%">\n'
        '<hr style="border:1px dashed #A2CD5A" width="50%" color=#A2CD5A SIZE=3>\n')
    filtered_data, filtered_header = read_table(filtered_stat)
    filtered_df = pandas.DataFrame(filtered_data, columns=filtered_header)
    # body += filtered_df.to_html(index=False)
    tmp = filtered_df.to_html(index=False)
    tmp = re.sub('<table border="1" class="dataframe">', '<table border="1" width="80%" class="dataframe" style="text-align: right; margin:auto"><caption>表2：过滤后测序数据基本信息统计表</caption>', tmp)
    body += tmp

    body += ('<h3>2. Reads长度-质量值分布图</h3>\n'
            '<hr style="border:3px dashed #A2CD5A; height:3px" SIZE=3 width="50%">\n'
            '<hr style="border:1px dashed #A2CD5A" width="50%" color=#A2CD5A SIZE=3>\n')

    if os.path.isdir(os.path.join(os.path.dirname(raw_stat), 'quality_control')):
        qc_path = os.path.join(os.path.dirname(raw_stat), 'quality_control')
        for item in os.listdir(qc_path):
            if item.endswith('.png') and item.startswith('filtered_'):
                if item.startswith('none_') or item.startswith('filtered_none_'):
                    continue
                # body += '<img src=\"{}\">\n'.format(os.path.join(qc_path, item))
                body += '<img src=\"./{}\" height="40%" width="40%"><br />\n'.format(os.path.join('quality_control', item))
    else:
        qc_path = os.path.dirname(raw_stat)
        for item in os.listdir(qc_path):
            if item.endswith('.png') and item.startswith('filtered_'):
                if item.startswith('none_') or item.startswith('filtered_none_'):
                    continue
                # body += '<img src=\"{}\">\n'.format(os.path.join(qc_path, item))
                body += '<img src=\"./{}\" height="40%" width="40%">\n'.format(item)

    body += '</div>'
    html_out = buildDOC(body)
    write_to_file(html_out, os.path.join(os.path.dirname(raw_stat), 'reads_stat.html'))


def main(outdir, min_quality=7, min_len=2000, max_len=None):
    statistics(outdir)
    to_html(os.path.join(outdir, 'raw_reads_stat.xls'), os.path.join(outdir, 'filtered_reads_stat.xls'), min_quality, min_len, max_len)


if __name__ == '__main__':
    main(sys.argv[1])
