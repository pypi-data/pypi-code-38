import csv
import numpy
import os

class DataSaver:
    def __init__(self, filename, divider =','):
        self.titles = None
        self.divider = divider
        self.filename = filename + '.csv'

        self.dir = os.path.dirname(self.filename)
        if not  os.path.isdir(self.dir):
            os.makedirs(self.dir)

    def writeTitles(self, *titles):
        if not os.path.isfile(self.filename):        
            with open(self.filename, 'w') as file:
                file.write(self.divider.join(self.titles))

    def newLine(self, data, *rest):
        row = []

        for title in self.titles:
            value = data[title]
            if isinstance(value, int) or isinstance(value, float) or isinstance(value, numpy.int64) or isinstance(value, numpy.float32):
                strValue = str(value)
            elif isinstance(value, str):
                strValue = value
            else:
                strValue =  ' '.join(str(x) for x in value)
            row.append(strValue)

        return self.divider.join(row)

    def add(self, data):
        # import pdb; pdb.set_trace()
        if (not self.titles):
            self.titles = data.keys()
            self.writeTitles(*self.titles)

        with open(self.filename, 'a') as file:
            file.write('\n')
            file.write(self.newLine(data))
