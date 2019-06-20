'''
Created on Aug 17, 2018

@author: reynolds
'''

class FileLogger(object):
    ''' Writes data to a file
    '''
    def __init__(self):
        ''' Constructor '''
        self.file = None

    def open(self,filename,ftype='w+',append=False):
        ''' Opens the file'''
        print('Opening ' + filename + ' ... ',end='')
        self.file = open(filename,ftype)
        print('Done')
        
    ''' writes a string to the file '''
    def write(self,string):
        if not self.file.closed:
            self.file.write(string)
        
    ''' Indicates whether the file is logging '''
    def isLogging(self):
        return self.file is not None
    
    ''' Closes the file '''
    def close(self):
        if self.file is None:
            return
        print('Closing ' + str(self.file.name) + ' ... ',end='')
        self.file.close()
        self.file = None
        print('Done')