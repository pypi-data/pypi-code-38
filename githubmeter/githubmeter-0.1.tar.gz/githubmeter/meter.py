import requests
import json
import math
import pandas as pd
# from operator import add 
import operator
# from statistics import mean 
import statistics

def parsed_api(url):
    response = requests.get(url)
    data = response.text
    parsed = json.loads(data)
    
    return parsed

def count_state(api_data):
#     arr = [] #array
    data = {} #dictionary{key:value}
    count = 0
    user_state = {}
    
    for i in range (len(api_data)):
        temp = api_data[i]['user']['login'] #temp untuk menyimpan nama developer
        count+=1
        if temp not in data: #jika temp tidak ada dalam dictionary, dia belum jadi key
            data[temp] = set() #set temp sebagai key dalam dictionary
        data[temp].operator.add(count) #tambahkan value untuk key yang saat ini
        
    for user, value in data.items(): #dictionary di looping sebanyak panjang dictionary
        user_state[user] = set() #set user sebagai key dalam dictionary user_state
        user_state[user] = len(value) #tambahkan value dalam key user_state sepanjang nilai value
    
    return user_state

def count_state_commit(api_data):
#     arr = [] #array
    data = {} #dictionary{key:value}
    count = 0
    user_state = {}
    
    for i in range (len(api_data)):
        temp = api_data[i]['author']['login'] #temp untuk menyimpan nama developer
        count+=1
        if temp not in data: #jika temp tidak ada dalam data dictionary, dia belum jadi key
            data[temp] = set() #set temp sebagai key dalam dictionary
        data[temp].add(count) #tambahkan value untuk key yang saat ini
        
    for user , value in data.items(): #dictionary di looping sebanyak panjang dictionary
        user_state[user] = set() #set user sebagai key dalam dictionary user_state
        user_state[user] = len(value) #tambahkan value dalam key user_state sepanjang nilai value
        
    return user_state

# def performance_issue(df):
    
#     issue_score = df.assign(issue_score = df['Issue Total']*30)
#     return issue_score

def performance_issue(df):
    issue_score = df.assign(issue_score = df['Issue Total'] / df['Issue Total'].statistics.mean())
    return issue_score

def performance_pull(df):
    pull_score = df.assign(pull_score = df['PR Total'] / df['PR Total'].statistics.mean())
    return pull_score

def performance_commit(df):
    commit_score = df.assign(commit_score = df['Commit Total'] / df['Commit Total'].statistics.mean())
    return commit_score


def count_loc(api_commit):
    
#     temp = {}
    locArr = []
    for i in range(len(api_commit)):
        a = api_commit[i]['weeks']
        arrA = []
        for j in range(len(api_commit[i]['weeks'])):
            tempDict = api_commit[i]['weeks'][j]
            arr = []
            for key, value in tempDict.items():
                arr.append(value)
            arrA.append(arr)
        locArr.append(arrA)
        
    ArrAdd = []
    ArrDel = []
    for i in range(len(locArr)):
        tempArr= []
        tempArr2=[]
        for j in range(len(locArr[i])):
            tempArr.append(locArr[i][j][1])
            tempArr2.append(locArr[i][j][2])
            #print(j)

        ArrAdd.append(tempArr)
        ArrDel.append(tempArr2)
        
    result_list = []
    
    for i in range(len(ArrAdd)):
        result_list.append(list(map(add, ArrAdd[i], ArrDel[i])))
        
        
    loc_tot = [ ]
    for i in range(len(result_list)):
        loc_tot.append(sum(result_list[i]))
        
    LOC_dict = {}

    for i in range(len(loc_tot)):
        developer = api_commit[i]['author']['login']
        LOC_dict[developer] = loc_tot[i]
        
    return LOC_dict

def performance_LOC(df):
    
    loc_score = df.assign(loc_score = df['LOC Total'] / df['LOC Total'].statistics.mean())
    return loc_score
