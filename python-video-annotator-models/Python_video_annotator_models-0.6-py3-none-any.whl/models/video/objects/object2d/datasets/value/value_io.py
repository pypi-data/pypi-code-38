import os, csv
from pythonvideoannotator_models.models.video.objects.object2d.datasets.value.value_base import ValueBase

class ValueIO(ValueBase):

    FACTORY_FUNCTION = 'create_value'

    ######################################################################################
    #### IO FUNCTIONS ####################################################################
    ######################################################################################

    def __len__(self):
        if self.filepath: self.__lazy_load()
        return super().__len__()
    def __getitem__(self, index): 
        if self.filepath: self.__lazy_load()
        return super().__getitem__(index)

    @property
    def values(self):
        if self.filepath: self.__lazy_load()
        return ValueBase.values.fget(self)
    @values.setter
    def values(self, values):
        self.filepath = None
        return ValueBase.values.fset(self, values)


    def __lazy_load(self):
        with open(self.filepath, 'rb') as infile:
            self.filepath = None
            infile.readline()
            for i, line in enumerate(infile):
                csvrow = line[:-1].split(b';')

                if csvrow[1] is None: continue
                if len(csvrow[1])==0: continue
                if csvrow[1]=='None': continue

                frame = int(csvrow[0])
                value = eval(csvrow[1])
                self.set_value(frame, value)


    def save(self, data, dataset_path=None):
        data = super(ValueIO, self).save(data, dataset_path)

        dataset_file = os.path.join(dataset_path, 'values.csv')
        with open(dataset_file, 'wb') as outfile:
            outfile.write((';'.join(['frame','value'])+'\n' ).encode( ))
            for index in range(len(self)):
                val = self.get_value(index)
                row = [index] + [val]
                outfile.write((';'.join( map(str,row) )).encode( ) )
                outfile.write(b'\n')

        return data

    def load(self, data, dataset_path=None):
        data = super(ValueIO, self).load(data, dataset_path)

        dataset_file = os.path.join(dataset_path, 'values.csv')

        # Fix a bug where files previously were saved with the extension cvs
        if not os.path.exists(dataset_file):
            dataset_file = os.path.join(dataset_path, 'values.cvs')

        self.filepath = dataset_file
        
        


    def import_csv(self, filename, first_row=0, col_frame=0, col_value=1):

        with open(filename, 'U') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            spamreader = csv.reader(csvfile, dialect)
            
            for i in range(first_row): next(spamreader, None)  # skip the headers
            
            for row in spamreader:
                if len(row)==0: break
                frame, value = row[col_frame], row[col_value]
                frame = int(frame)
                value = None if value=='None' or value.strip()=='' else float(value)
                self.set_value(frame, value)