'''
Created on 2017年9月16日

@author: caifh
'''
import xlrd


class Ctype:
    empty = 0
    string = 1
    number = 2
    date = 3
    boolean = 4
    error = 5


class LabelTable:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = xlrd.open_workbook(self.file_path)
        self.sheets = self.data.sheets()
        self.labels = None
    
    def get_label_index(self, label, sheet_index=0, row_index=0):
        labels = self.get_labels(sheet_index, row_index)
        return labels.index(label)
    
    def get_labels(self, sheet_index=0, row_index=0):
        if self.labels is None:
            self.labels = []
            row_slice = self.sheets[sheet_index].row_slice(row_index)
            item_index = 0
            for item in row_slice:
                if item.ctype == Ctype.string:
                    self.labels.append(item.value)
                else:
                    self.labels.append(None)
                    print('sheet {} row {} item {} ctype is {}!'.format(sheet_index, row_index, item_index))
                
                item_index += 1
        
        return self.labels
    
    def get_table(self, sheet_index=0):
        return self.sheets[sheet_index]