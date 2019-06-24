import csv


class CSVRW:
    def __init__(self, path, delimiter):
        self.path = path
        self.delimiter = delimiter

    def read(self, ignore=0):
        ls = []
        with open(self.path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter)
            counter = 0
            for row in reader:
                if counter < ignore:
                    counter = counter + 1
                    continue
                ls.append(row)
        return ls

    def write(self, table, header=True):
        with open(self.path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter)
            if header:
                writer.writerow(table[0].keys())
            for row in table:
                writer.writerow(row)
