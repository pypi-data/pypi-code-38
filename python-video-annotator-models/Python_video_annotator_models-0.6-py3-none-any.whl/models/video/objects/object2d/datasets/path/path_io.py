import os, csv, math
from pythonvideoannotator_models.models.video.objects.object2d.datasets.path.path_base import PathBase

class PathIO(PathBase):

    FACTORY_FUNCTION = 'create_path'


    ######################################################################################
    #### IO FUNCTIONS ####################################################################
    ######################################################################################

    def save(self, data, dataset_path=None):

        dataset_file = os.path.join(dataset_path, 'path.csv')
        with open(dataset_file, 'wb') as outfile:
            outfile.write((';'.join(['frame','x','y'])+'\n').encode())
            for index in range(len(self)):
                pos = self.get_position(index, use_referencial=False)
                was_modified = self.was_modified(index)
                was_switched = self.was_identity_switched(index)
                row = [index] + ([None, None] if pos is None else list(pos)) + [was_modified, was_switched]
                outfile.write((';'.join( map(str,row) )).encode( ))
                outfile.write(b'\n')

        # save the referencial data
        data['apply-referencial'] = self.apply_referencial
        data['referencial-point'] = self.referencial
        data['show-name']         = self.show_name
        data['show-object-name']  = self.show_object_name
        data['color']             = self.color

        data = super(PathIO,self).save(data, dataset_path)
        return data

    def load(self, data, dataset_path=None):
        data = super(PathIO, self).load(data, dataset_path)

        dataset_file = os.path.join(dataset_path, 'path.csv')

        # Fix a bug where files previously were saved with the extension cvs
        if not os.path.exists(dataset_file):
            dataset_file = os.path.join(dataset_path, 'path.cvs')

        with open(dataset_file, 'U') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(2048))
            csvfile.seek(0)
            spamreader = csv.reader(csvfile, dialect, delimiter=';')

            next(spamreader)
            for row in spamreader:
                frame = int(row[0])
                x = None if row[1] == 'None' or row[1].strip() == '' else float(row[1])
                y = None if row[2] == 'None' or row[2].strip() == '' else float(row[2])
                was_modified = row[3] if len(row)>3 else False
                was_switched = row[4] if len(row)>4 else False

                # does not the set the coordinates if they are None
                if x is not None and y is not None and x!='None' and y!='None':
                    self.set_position(frame, float(x), float(y))

                if frame >= len(self._modified):
                    self._modified += [False] * (frame+1-len(self._modified))
                self._modified[frame] = was_modified or was_modified=='True'

                if frame >= len(self._identity_switched):
                    self._identity_switched += [False] * (frame+1-len(self._identity_switched))
                self._identity_switched[frame] = was_switched or was_switched=='True'


        # load the referencial data
        ref                     = data.get('referencial-point', None)
        self.referencial        = tuple(ref) if ref else None
        self.apply_referencial  = data.get('apply-referencial', False)
        self.show_name          = data.get('show-name', False)
        self.show_object_name   = data.get('show-object-name', False)
        self.color              = data.get('color', self.color)

        return data






    def import_csv(self, filepath, first_row=0, col_frame=0, col_x=1, col_y=2):
        """
        Import path from a CSV file.

        :param str filepath: Path of the file to import.
        :param int first_row: First row index with data.
        :param int col_frame: Column index with the frame index.
        :param int col_x: Column index of the x coordinate.
        :param int col_y: Column index of the y coordinate.
        """
        with open(filepath, 'U') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(2048))
            csvfile.seek(0)
            spamreader = csv.reader(csvfile, dialect)
            
            for i in range(first_row): next(spamreader, None)  # skip the headers

            count = 0
            
            for row in spamreader:
                if len(row)==0: break
                if col_frame<0:
                    x, y  = row[col_x], row[col_y]
                    frame = count
                    count += 1
                else:
                    frame, x, y = row[col_frame], row[col_x], row[col_y]
                    frame = int(frame)
                x = None if x=='None' or x.strip()=='' else float(x)
                y = None if y=='None' or y.strip()=='' else float(y)

                if x is not None and y is not None and not math.isnan(x) and not math.isnan(y):
                    self.set_position(frame, x, y)

            self._modified = []          # store all the frames where there were manual modifications.
            self._identity_switched = [] # store all the identification switches