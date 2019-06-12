import json
import os
import sys

# FUNGSI PREPROCESSING
# PARAMETER
# hasil crawling
def preproses(textn):
    hasil = {}
    pre = {}

    # CASE FOLDING
    casefold = textn.casefold()

    # TOKENIZING 
    tokens = casefold.split()
    
    hasil["hasil"] = tokens
    
    pre['cf'] = casefold
    pre['hasil'] = hasil

    return pre

def input_kategori(kat):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    dictionaryFile = current_dir + '/data/kategori.json'
    file = dictionaryFile
    kategori = [[0 for x in range(len(kat))] for x in range(len(kat))]

    if os.stat(file).st_size > 0:
        f = open(file, 'r+')
        f.truncate(0)

    for i in range(len(kat)):
        kategori[i] = {"kategori" : kat[i]}

    with open(file, 'r+') as outfile:  
        json.dump(kategori, outfile)
        outfile.close()
    
    return kategori

def input_sub(kategori, asp):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    dictionaryFile = current_dir + '/data/kategori.json'
    file = dictionaryFile
    
    with open(file, 'r') as outfile: 
        data = json.load(outfile)
    
    print(data)
    
    for z in range(len(data)):
        print()
        if data[z]['kategori'] == kategori:
            data[z]['sub_kategori'] = []
            for a in range(len(asp)):
                data[z]["sub_kategori"].append({
                    "nama_sub" : asp[a]
                })
                
    print(data)
    
    with open(file, 'w') as outfile:  
        json.dump(data, outfile)
        outfile.close()
        
    return data
        

# FUNGSI SPOKS 
# PARAMETER
# hasil preprocessing

def spoks(hasil):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    kt = current_dir + '/data/kategori.json'
    ad = current_dir + '/data/adjective.json'

    with open(kt) as f:
        aspek = json.load(f)

    with open(ad) as g:
        sif = json.load(g)
    
    ret = {}
    sis = {}
    th = {}
    jum = {}
    syn_ = {}
    ant_ = {}
    c = {}
    jumlah = {}
    avg = {}
    maks = 5
    cr = {}
    
    for asp in aspek:
        sis[asp['kategori']] = {}
        th[asp['kategori']] = {}
        jum[asp['kategori']] = {}
        syn_[asp['kategori']] = {}
        ant_[asp['kategori']] = {}
        c[asp['kategori']] = 0
        jumlah[asp['kategori']] = 0
        avg[asp['kategori']] = 0
        
        for sub in asp['sub_kategori']:

            jum[asp['kategori']][sub['nama_sub']] = 0

            for adj in sif:

                if sub['nama_sub'] in adj['synset'].split(','):

                    syn_[asp['kategori']][sub['nama_sub']] = adj['synset'].split(',')
                    ant_[asp['kategori']][sub['nama_sub']] = adj['antset'].split(',')

                    for has in hasil['hasil']:
                        if has==sub['nama_sub']:
                            jum[asp['kategori']][sub['nama_sub']] = jum[asp['kategori']][sub['nama_sub']]+1

                        for synset in syn_[asp['kategori']][sub['nama_sub']]:
                            if has == synset:
                                jum[asp['kategori']][sub['nama_sub']] = jum[asp['kategori']][sub['nama_sub']]+1

                        for antset in ant_[asp['kategori']][sub['nama_sub']]:
                            if has == antset:
                                jum[asp['kategori']][sub['nama_sub']] = jum[asp['kategori']][sub['nama_sub']]-1

            #SC Val
            sc = jum[asp['kategori']][sub['nama_sub']]
            sis[asp['kategori']][sub['nama_sub']] = sc
            print('Nama Kategori : '+str(asp['kategori']))
            print('SC Val '+sub['nama_sub']+' : '+str(sc))

            #TH
            if sc >= 1:
                th[asp['kategori']][sub['nama_sub']] = 1
            if sc < 0:
                th[asp['kategori']][sub['nama_sub']] = -1
            if sc == 0:
                th[asp['kategori']][sub['nama_sub']] = 0
            
            print('TH '+str(asp['kategori'])+' : '+str(th[asp['kategori']][sub['nama_sub']]))

            #C
            c[asp['kategori']] = c[asp['kategori']] + th[asp['kategori']][sub['nama_sub']]
            print('C '+str(asp['kategori'])+' : '+str(c[asp['kategori']]))

            #Average
            jumlah[asp['kategori']] = len(asp['sub_kategori'])
            avg[asp['kategori']] = c[asp['kategori']]/jumlah[asp['kategori']]
            print('Jumlah '+str(asp['kategori'])+' : '+str(jumlah[asp['kategori']]))

            print('AVG '+str(asp['kategori'])+' : '+str(avg[asp['kategori']]))
        
    #CR
    cx = 0
    for avgs in aspek:
        cr[avgs['kategori']] = avg[avgs['kategori']] * maks
        print('CRR : '+str(cr[avgs['kategori']]))
        
        cx = cx+cr[avgs['kategori']]
    
    print('CR : '+str(cx))

    # RATING
    fr = cx/len(aspek)
    print('Rating : '+str(fr))

    # END COMMENT
    
    ret['scv'] = sis
    ret['th'] = th
    ret['c'] = c
    ret['avg'] = avg
    ret['cr'] = cr
    ret['fr'] = fr
    ret['aspek'] = aspek

    print(sis)

    return ret