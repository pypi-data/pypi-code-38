###############
##  IMPORTS  ##
###############

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from datetime import datetime
from bs4 import BeautifulSoup
from pprint import pprint
import numpy as np
import unicodedata
import requests
import random
import ujson
import time
import math
import json
import copy
import ast
import sys
import re
import os

###############################
##  TEXT CLEANING FUNCTIONS  ##
###############################

# Remove Non-Ascii Characters
def clean_string(string):
    string = unicodedata.normalize('NFKD',string).encode('ascii','ignore').decode("utf-8")
    string = string.replace('\\u','u:')
    return string

# Cleaning Punctuation
def clean_punctuation(string):
    string = string.replace('(',' ( ').replace(')',' ) ').replace('[',' [ ').replace(']',' ] ')
    string = string.replace(',',' , ').replace(';',' ; ').replace(':',' : ').replace("'"," ' ")
    string = string.replace('<',' < ').replace('>',' > ').replace('%',' % ')
    string = string.replace('\t',' ').replace('\r',' ').replace('\n',' ')
    string = string.replace('. ',' . ').replace('! ',' ! ').replace('? ',' ? ')
    if string[-1] in ['.','!','?']: string = string[0:-1]
    string = re.sub('[ ]{2,}', ' ', string)
    string = string.strip()
    return string

# Join Token Into Bigrams Where Possible
def collapse_bigrams(title, valid_bigrams):
    ln_t = len(title)
    bgrm_title = []; loop_counter = 0
    if ln_t == 1: return title
    while loop_counter < (ln_t-1):
        i = loop_counter
        if title[i] + '_' + title[i+1] in valid_bigrams:
            bgrm_title.append(title[i] + '_' + title[i+1])
            loop_counter += 1
        else:
            bgrm_title.append(title[i])
            if i == (ln_t-2): bgrm_title.append(title[i+1])
        loop_counter += 1
    return bgrm_title

###################################
##  FOLDER PROCESSING FUNCTIONS  ##
###################################

# Removing Contents From A Folder
def clear_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path): os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

##############################
##  WEB SCRAPING FUNCTIONS  ##
##############################

# Pulling Webpage Content
def pull_webpage(url, session_requests, method, cookie):
    headers = random_user_agents()
    try:
        page = session_requests.get(url, cookies={'cookie': cookie}, headers=headers)
        soup = BeautifulSoup(page.content, method)
    except:
        print('webpage pull failed; retrying in 3 seconds')
        time.sleep(3)
        page = session_requests.get(url, cookies={'cookie': cookie}, headers=headers)
        soup = BeautifulSoup(page.content, method)
    return soup

# Pulling A Random User Agent
def random_user_agents():
    user_agents = []
    f = open('user_agents.txt','r')
    for line in f:
        row = line.replace('\n','')
        user_agents.append(row)
    roll = random.randint(0, len(user_agents)-1)
    user_agent = {'User-Agent': user_agents[roll]}
    return user_agent

##############################
##  DATA LOADING FUNCTIONS  ##
##############################

# Grabbing Mapping From Words To Ids
def grab_mapping(file_name):
    # Loading Mapping
    f_mapping = open(file_name,'r')
    for line in f_mapping: mapping = ast.literal_eval(line.replace('\n',''))
    f_mapping.close()
    return mapping


# Grabbings Vector Embeddings For Each Vocab Word
def grab_vocab_embeddings(directory):
    # Loading Embeddings
    print('Loading model helper data...')
    vocab_embeddings = []
    f_vocab_embeddings = open(os.path.join(directory, 'embedding_vectors.txt'),'r')
    for line in f_vocab_embeddings:
        vector = np.asarray(ast.literal_eval(line.replace('\n','')))
        vocab_embeddings.append(vector)
    # Adding 0-Vector Embedding
    len_embeddings = len(vocab_embeddings[0])
    vocab_embeddings.append([0.0]*len_embeddings)
    zero_idx = len(vocab_embeddings) - 1
    # Returning Output
    vocab_embeddings = np.asarray(vocab_embeddings)
    return vocab_embeddings, zero_idx


# Opening Data Files
def open_data_files(data_type, parent_dir, dset):
    print('Opening ' + dset + ' ' + data_type + '...')
    file_name = os.path.join(parent_dir, dset + '_data', dset + '_' + data_type + '.txt')
    f = open(file_name, 'r')
    return f, file_name


################################
##  MODEL TRAINING FUNCTIONS  ##
################################

# Balancing Classes Among Data Samples
def class_balance(data, balance, method, max_size):
    print('Balancing classes...')
    # Finding Largest Class For Determining Class Size
    classes = {}
    for label in data['labels']:
        label_v = np.argmax(label)
        if label_v not in classes: classes[label_v] = 0
        classes[label_v] = classes[label_v] + 1
    class_size = max(classes.values()) if method == 'max' else min(classes.values())
    class_size = min(class_size,max_size)
    min_class_size = min(classes.values())
    iterations = int(math.ceil(class_size / min_class_size)) if balance == True else 1
    print('Pre-Class balance: ' + str(classes))
    # Pulling Necessary Samples
    new_data = { key:[] for key in data if 'file' not in key }
    classes = {}; samples = 0.0
    for m in range(0,iterations):
        for i in range(0,len(data['labels'])):
            label = data['labels'][i]
            label_v = np.argmax(label)
            if label_v not in classes: classes[label_v] = 0
            if classes[label_v] >= class_size: continue
            classes[label_v] = classes[label_v] + 1
            samples = samples + 1.0
            for key in new_data: new_data[key].append(data[key][i])
    # Return Output
    for key in new_data: new_data[key] = np.asarray(new_data[key])
    for key in data:
        if key not in new_data: new_data[key] = data[key]
    new_data['data'] = new_data['data'].astype(np.float32)
    print('Class balance: ' + str(classes))
    for cl in classes: print('Class ' + str(cl) + ' percentage: ' + str(classes[cl] / samples))
    return new_data, classes

# Randomize Data
def randomize_data(data):
    print('Randomizing data...')
    # Randomizing
    rand_data = { key:[] for key in data if 'file' not in key }
    ordering = [j for j in range(0,len(data['labels']))]
    random.shuffle(ordering)
    for j in range(0,len(data['labels'])):
        cur_idx = ordering[j]
        for key in data:
            if 'file' not in key: rand_data[key].append(data[key][cur_idx])
    # Return
    for key in rand_data: rand_data[key] = np.asarray(rand_data[key])
    for key in data:
        if key not in rand_data: rand_data[key] = data[key]
    rand_data['data'] = rand_data['data'].astype(np.float32)
    return rand_data

# Data Augmenting
def data_augmenting(data, augs):
    print('Augmenting data...')
    data_stats = { j:[] for j in range(0,len(data['data'][0][0])) }
    for i in range(0,30000):
        for row in data['data'][i]:
            for j in range(0,len(row)):
                data_stats[j].append(row[j])
    for key in data_stats: data_stats[key] = {'std':np.std(data_stats[key])}
    new_data = { key:[] for key in data }
    new_data['original'] = []
    for i in range(0,len(data['labels'])):
        for key in data: new_data[key].append(data[key][i])
        new_data['original'].append(1)
        aug = augs[data['labels'][i]]
        for s in range(0,aug):
            cur = copy.deepcopy(data['data'][i])
            for r in range(0,len(cur)):
                for j in range(0,len(cur[r])):
                    if random.random() < 0.1:
                        cur[r][j] = cur[r][j] + ( (data_stats[j]['std'] * 0.0627) * (2*random.random()-1) )
            for key in data:
                if key == 'data': new_data[key].append(cur)
                else: new_data[key].append(data[key][i])
            new_data['original'].append(0)
    for key in new_data: new_data[key] = np.asarray(new_data[key])
    new_data['data'] = new_data['data'].astype(np.float32)
    return new_data

##########################
##  PLOTTING FUNCTIONS  ##
##########################

# Drawing Scatter Plot Visualization
def create_scatter_plot(df, x_columns, y_columns, constraints, labels, script_name, alt_filename = ''):
    base_folder = script_name.replace('.py', '')
    if script_name[0] != '/': script_name = '/' + script_name
    filename = '/' + alt_filename if alt_filename != '' else script_name.replace('.py','.png').replace(os.getcwd(), '')
    num_subplots = max([ int(constraints[i][2].replace('ax','')) if len(constraints[i]) > 2 else 1
                         for i in range(0,len(x_columns)) ])
    f, axarr = plt.subplots(num_subplots, sharex=True)
    f.set_figheight(5 * num_subplots - num_subplots)
    f.set_figwidth(5)
    y_max = 0.0
    colors = [
        'blue', 'purple', 'red', 'green',
        'magenta', 'cyan', 'black', 'orange',
        'deepskyblue', 'crimson', 'coral', 'limegreen',
        'darkslategray', 'indigo', 'orchid', 'seagreen'
    ]
    for i in range(0,len(x_columns)):
        xs = df[x_columns[i]].tolist()
        ys = df[y_columns[i]].tolist()
        ls = df[labels[i]].tolist()
        cs = df[constraints[i][0]].tolist()

        xs = [ xs[j] for j in range(0,len(xs)) if cs[j] == constraints[i][1] ]
        ys = [ ys[j] for j in range(0,len(ys)) if cs[j] == constraints[i][1] ]
        ls = [ ls[j] for j in range(0,len(ls)) if cs[j] == constraints[i][1] ]

        label = max(ls)
        title = y_columns[i] + ' vs ' + x_columns[i]
        axis = constraints[i][2] if len(constraints[i]) > 2 else 'ax1'
        if num_subplots == 1: axis = axarr
        else: axis = axarr[int(axis.replace('ax',''))-1]

        axis.scatter(xs, ys, c=colors[i], label=label)
        axis.plot(xs, ys, c=colors[i])
        axis.set_ylim(ymin=0)
        if max(ys) > y_max:
            margin = (max(ys) - min(ys)) / 10.0
            y_max = max(ys) + margin
            axis.set_ylim(ymax=y_max)
        axis.set_title(title)
        axis.legend(loc=1)

    plt.xticks(rotation=70)
    plt.xlabel(x_columns[0])
    f.tight_layout()
    plt.savefig(base_folder + filename)
    return
