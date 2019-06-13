import csv
import codecs
try:
    from StringIO import StringIO
except Exception as e:
    from io import StringIO
import tempfile


from six import PY2, iteritems
if not PY2:
    from six import u as unicode

import logging,datetime
l = logging.getLogger("ppss.pyramidutils.utf8csv")


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        '''next() -> unicode
        This function reads and returns the next line as a Unicode string.
        '''
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.l = logging.getLogger(self.__class__.__name__)
        #self.l = logging.getLogger("main")

    def writerow(self, row):
        try:
            r=1
            self.writer.writerow([s.encode("utf-8") for s in row])
            # Fetch UTF-8 output from the queue ...
            r=2
            data = self.queue.getvalue()
            r=3
            data = data.decode("utf-8")
            # ... and reencode it into the target encoding
            r=4
            data = self.encoder.encode(data)
            # write to the target stream
            r=5
            self.stream.write(data)
            # empty queue
            r=6
            self.queue.truncate(0)
        except Exception as e:
            #print row,e,r
            #raise e
            self.l.error("inner errore, errore!!")
            self.l.error("step:"+unicode(r)+ " " + e.message + repr(e)+ "--" + repr(row)    )
            pass

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class Exporter(object):
    def __init__(self,evcollection,titles,parserows=True,delimiter = ',',getter=None,datetimeformat = "%Y-%m-%d"):
        #self.evl = [x.getMap() for x in evcollection]
        self.titles = titles

        if parserows:
            evrows = []
            for ev in evcollection:
                row = []
                for k in self.titles:
                    try:
                        if getter:
                            val = getter(ev,k)
                        else:
                            val = ev.getVal(k)
                    except Exception as e:
                        l.warning("key {key} not in row {row}, exception {e}".format(key=k, row=str(row), e=e ))
                        val = ""
                    if isinstance(val,datetime.datetime) or isinstance(val,datetime.date):
                        val = unicode(val.strftime(datetimeformat))
                    if not (isinstance(val,str) or isinstance(val,unicode)):
                        val = unicode(val)
                    row.append(val)
                evrows.append(row)
        else:
            evrows = evcollection
        self.evl = evrows
        self.delimiter = delimiter
        if PY2:
            self.retfile = tempfile.NamedTemporaryFile()
        else:
            self.retfile = tempfile.NamedTemporaryFile(mode='w')


    def writeAll(self, delimiter = None):
        d = delimiter if delimiter else self.delimiter if self.delimiter else ','
        if PY2:
            w = UnicodeWriter(self.retfile, delimiter=d, quoting=csv.QUOTE_ALL)
        else:
            w = csv.writer(self.retfile, dialect=csv.excel, delimiter = d)
        w.writerow(self.titles)
        for maprow in self.evl:
            l.info("*******{row}".format(row=maprow) )
            w.writerow(maprow)
        self.retfile.seek(0, 0)
        return self.retfile


class Importer(object):
    titlepos = {}
    rows = []
    header = []

    def __init__(self, fn, mapping=None, delimiter=",", headertransform=None):
        self.titlepos = {}
        self.rows = []
        #f = codecs.open(fn, "r", "utf-8")  #open(fn,'r')
        if PY2:
            self.csvreader = UnicodeReader(open(fn,'rb'),delimiter=delimiter)
        else:
            self.csvreader = csv.reader(open(fn,'r'), dialect=csv.excel,delimiter=delimiter)
        #self.csvreader = csv.reader(f,delimiter=";")
        
        h = next(self.csvreader)
        if headertransform:
            h = [headertransform(x) for x in h]
        self.header=h 
        l.debug("header:"+repr(h))
        for i in range(len(h)):
            self.titlepos[ h[i].strip() ] = i
        for row in self.csvreader:
            try:
                thisrow = {}
                for key,val in iteritems(self.titlepos):
                    if mapping :
                        l.debug(mapping)
                        thisrow[mapping[key]] = row[val].strip()
                    else:
                        l.debug(key)
                        thisrow[key] = row[val].strip()

                l.debug("*read:"+repr(thisrow))
                self.rows.append(thisrow)
            except Exception as  e:
                l.error("error reading:{error}\nrow:{row}".format(error=repr(e),row=row) )
                raise e


    def getRows(self):
        return self.rows

