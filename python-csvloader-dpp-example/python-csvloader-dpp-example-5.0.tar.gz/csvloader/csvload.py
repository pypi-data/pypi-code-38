import csv
import pandas

def load_csv(path):
    with open(path,'rt')as f:
        data = csv.reader(f)
        for row in data:
            print(row)

def load_pandas(path):
    result = pandas.read_csv(path)
    print(result)