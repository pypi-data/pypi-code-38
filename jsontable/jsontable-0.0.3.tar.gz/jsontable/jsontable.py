# -*- coding: utf-8 -*-
"""
JSON to Table converter
Author: Ernesto Monroy
Created: 10/06/2019
"""
import json

class converter:
    
    def __init__(self):
        self.paths=[]
        self.records=[[]]
        self.json_content={}
        self.column_names=[]
        self.column_numbers=dict()


    #Function to "set" the mapping and pass it to the recursive function
    def set_paths (self, mapping):
        #Clear previous mapping
        self.paths=[]
        #Sort columns by path
        sorted_columns=sorted(mapping, key = lambda p: next(iter(p)))
        #Loop all columns
        for c in sorted_columns:
            #Full path
            path=next(iter(c))
            #Expand each path
            current_path=[]
            for node in path.split('.'):
                current_path+=[node.strip()]
            self.paths+=[current_path]
            #Add column numbers
            self.column_numbers[c[path]]=len(self.column_names)
            #Add column names
            self.column_names+= [c[path]]

        return self.paths

    
    #Function to convert a json object to a table
    def convert_json (self, in_content):
        #Check for mapping
        if self.paths==[]:
            raise Exception('The mapper is missing valid paths. Make sure you set the mapping before calling this function with set_mapping(mappingJSON)')
        #Clear previous data
        self.records=[[]]
        #Set new data
        self.json_content=in_content
        for i in range(len(self.paths)):
                if i>0:
                    previous_path=self.paths[i-1][1:]
                else:
                    previous_path=[]
                self.records=self.recurse(self.paths[i][1:],self.json_content,self.records,previous_path)

        #Add column names
        return [self.column_names]+self.records


    def recurse (self,in_path,in_content,in_records=[[]],previous_path=[],append_list=False):
        #Whilst there are paths left to explore
        if len(in_path)>0:
            #If the node is a list, expand it
            if type(in_content)==list:
                if append_list:
                    new_record=[]
                    for i in range(len(in_records)):
                        new_record+=self.recurse(in_path,in_content[i],[in_records[i]],previous_path)
                    in_records=new_record
                else:
                    new_records=[]
                    for c in in_content:  
                        new_records+=self.recurse(in_path,c,in_records,previous_path)
                    in_records=new_records
            #Otherwise keep branching
            elif type(in_content)==dict:
                if (previous_path[0:1]==in_path[0:1]):
                    previous_path=previous_path[1:]
                    append_list=True
                #If the child exists, then continue
                if in_path[0] in in_content:
                    in_content=in_content[in_path[0]]
                    in_records=self.recurse(in_path[1:],in_content,in_records,previous_path,append_list)
                #Otherwise add a null
                else:
                    in_records=self.recurse([],None,in_records,previous_path)
            else:
                in_records=self.recurse([],None,in_records,previous_path)
        else:
            #Convert types
            if type(in_content)==list:
                if len(in_content)==0:
                    final_string=None
                elif type(in_content[0]) in [list,dict]:
                    final_string=json.dumps(in_content)
                else:
                    final_string=", ".join(str(x) for x in in_content)
            elif in_content==None:
                final_string=in_content
            else:
                final_string=str(in_content)
            new_record=[]
            for row in in_records:
                new_record+=[row+[final_string]]
            in_records=new_record
        return in_records