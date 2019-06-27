# import xml2py
#
# file = xml2py.deserialize('C:/Projects/Website-ASP.NET/pub/ReportData/Metadata/ACS 2013-5yr Metadata.xml')
# print(file)

simple = dict(int_list=[1, 2, 3],

              text='string',

              number=3.44,

              boolean=True,

              none=None)

from datetime import datetime


class A(object):

    def __init__(self, simple):

        self.simple = simple

    def __eq__(self, other):

        if not hasattr(other, 'simple'):
            return False

        return self.simple == other.simple

    def __ne__(self, other):

        if not hasattr(other, 'simple'):
            return True

        return self.simple != other.simple


complex = dict(a=A(simple), when=datetime(2016, 3, 7))

print('stop')