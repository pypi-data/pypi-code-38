#! /usr/bin/env python
# coding: utf-8
__author__ = 'huo'
import time
import requests

from jy_word.File import File
from jy_word.Word import Paragraph, Run, Set_page, Table, Tc, Tr, HyperLink
from jy_word.Word import uniq_list
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

my_file = File()

r = Run()
hyperlink = HyperLink()
r.family_en = 'Times New Roman'
p = Paragraph()
set_page = Set_page().set_page
table = Table()
tr = Tr()
tc = Tc()
gray = 'E9E9E9'
gray_lighter = 'EEEEEE'
blue = '00ADEF'
white = 'FFFFFF'
red = 'ED1C24'
orange = 'F14623'
colors = ['2C3792', '3871C1', '50ADE5', '37AB9C', '27963C', '40B93C', '80CC28']


# 初号=42磅
# 小初=36磅
# 一号=26磅
# 小一=24磅
# 二号=22磅
# 小二=18磅
# 三号=16磅
# 小三=15磅
# 四号=14磅
# 小四=12磅
# 五号=10.5磅
# 小五=9磅
# 六号=7.5磅
# 小六=6.5磅
# 七号=5.5磅
# 八号=5磅


# ##################下载报告所需方法######################



def write_gene_list():
    gene_items = get_gene_list()
    items = []
    for i in range(len(gene_items)):
        gene = gene_items[i]
        print i+1, gene, len(gene_items), format_time()
        items.append(get_gene_info(gene))
        my_file.write('data/1.2gene_list.json', items)
    return items


def get_gene_list():
    db_table = my_file.read('0.2.2.variant_anno.maf.xls', sheet_name='0.2.2.variant_anno.maf', dict_name='data/part1')
    items = db_table.col_values(0)[1:]
    items = uniq_list(items)
    return items


def get_gene_info(gene):
    summary = ''
    description = ''
    url1 = 'http://oncokb.org/api/v1/evidences/lookup?hugoSymbol=%s&evidenceTypes=GENE_SUMMARY' % gene
    url2 = 'http://oncokb.org/api/v1/evidences/lookup?hugoSymbol=%s&evidenceTypes=GENE_BACKGROUND' % gene
    data1 = my_request(url1)
    data2 = my_request(url2)
    item = {'hugoSymbol': gene}
    if data2 is not None:
        if len(data2) > 0:
            info = data2[0]
            if 'gene' in info:
                gene_info = info['gene']
                item.update(gene_info)
            if 'description' in info:
                description = info['description']
    if data1 is not None:
        if len(data1) > 0:
            if 'description' in data1[0]:
                summary = data1[0]['description']
    item['summary'] = summary
    item['description'] = description
    return item


def get_evidence():
    items = []
    gene_items = []
    gene_list = []
    for level in ['1', '2A', '3A', '4']:
        url1 = 'http://oncokb.org/legacy-api/evidence.json?levels=LEVEL_%s' % level
        data1 = my_request(url1)
        if data1 is not None:
            print level, len(data1[0])
            items += data1[0]
            for item in data1[0]:
                gene = item['gene']['hugoSymbol']
                if gene not in gene_list:
                    gene_list.append(gene)
                    gene_items.append(get_gene_info(gene))
    my_file.write('oncokb_evidence_level.json', items)
    print len(gene_items)
    my_file.write('oncokb_gene_info.json', gene_items)
    # my_file.write('oncokb_evidence_level.xls', items)
    return items


def my_request(url, r='json'):
    try:
        rq = requests.get(url)
    except:
        return None
    if rq.status_code == 200:
        if r == 'json':
            data = rq.json()
            return data
        return rq.text
    return None


def format_time(t=None, frm="%Y-%m-%d %H:%M:%S"):
    if t is None:
        t = time.localtime()
    if type(t) == int:
        t = time.localtime(t)
    my_time = time.strftime(frm, t)
    return my_time



# write_gene_list()
# get_evidence()


print my_request('https://www.snpedia.com/index.php?title=Special:Ask&offset=0&limit=500&q=%5B%5BCategory%3AIs+a+genotype%5D%5D&p=mainlabel%3D%2Fformat%3Dtable&po=%3FMagnitude%0A%3FRepute%0A%3FSummary%0A&sort=magnitude&order=desc', 'text')