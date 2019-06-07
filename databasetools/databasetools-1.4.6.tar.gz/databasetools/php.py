import os


class PHPArray:
    def __init__(self, data, destination, file_name=False, header_row=False):
        """
        Encode data as a sequential or associative PHP array.
        :param data: Multi-dimensional data container (list of lists, list of tuples, set of lists)
        :param destination: Destination folder
        :param header_row: Bool, if set to true first row will be used as keys and the array will be encoded
        associatively
        """
        self.data = data
        self.dst = destination
        if header_row:
            self.header = self.data.pop(0)
            self.array_func = self.associative
        else:
            self.array_func = self.sequential
        if file_name:
            self.file_name = file_name
        else:
            self.file_name = 'temp'
        self.create()

    def create(self):
        # Set text file
        text = os.path.join(self.dst, (str(self.file_name + '.txt')))
        try:
            text_file = open(text, "r+")
        except IOError:
            text_file = open(text, "w")
        text_file.truncate()

        # Write first two lines of PHP file
        text_file.write("<?php" + "\n")
        text_file.write("$items = array(" + "\n")

        # Iterate through input data and write each row
        for row in self.data:
            text_file.write('\tarray(')
            self.array_func(row, text_file)
            text_file.write("),\n")

        text_file.write(");\n ")
        text_file.write("\n" + "$items_count = count($items);")
        text_file.write("\n" + "?>")
        text_file.close()
        newname = text.replace('.txt', '.php')
        os.rename(text, newname)

    @staticmethod
    def sequential(row, text_file):
        for items in row:
            text_file.write('"' + str(items) + '"' + ',')

    def associative(self, row, text_file):
        for i in range(0, len(row)):
            text_file.write('"' + str(self.header[i]) + ' => ' + str(row[i]) + '"')
            if i is not len(row)-1:
                text_file.write(', ')
