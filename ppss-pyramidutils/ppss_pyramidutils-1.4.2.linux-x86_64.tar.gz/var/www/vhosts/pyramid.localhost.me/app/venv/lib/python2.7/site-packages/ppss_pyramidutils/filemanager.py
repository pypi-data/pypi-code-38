from .utils import Utils
import logging
l = logging.getLogger("ppss.pyramidutils")
import os,shutil,uuid,re,string,unicodedata

from six import PY2
if not PY2:
    from six import u as unicode

_valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

class FileManager(Utils):
    savepath = "/tmp/finale"
    tmppath = "/tmp"
    myconf = ['savepath','tmppath']

    def __init__(self):
        pass

    @classmethod
    def sanitizeFilename(cls,filename, whitelist=_valid_filename_chars, replace=' '):
        """Better safe than sorry: sanitize a filename replacing unsafe chars. 
            @filename: string to sanitize
            @whitelist: string containing safe chars in filename
            @replace: string containg valid chars that we prefer to substitute with an _
            returns: sanitized string"""
        # replace spaces
        for r in replace:
            filename = filename.replace(r,'_')
        
        # keep only valid ascii chars
        cleaned_filename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore').decode()
        
        # keep only whitelisted chars
        return ''.join(c for c in cleaned_filename if c in whitelist)

    @classmethod
    def slugify(cls,filename):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        import unicodedata
        value = unicodedata.normalize('NFKD', unicode(filename)).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        value = unicode(re.sub('[-\s]+', '-', value))
        return value

    @classmethod
    def saveToTmp(cls,requestfile):
        infile = requestfile.file
        #make sure it's not a malicious attack
        name = FileManager.sanitizeFilename( str(requestfile.name) )

        file_path = os.path.join(cls.tmppath, str(uuid.uuid4()) + name )
        l.debug("FileManager.saveToTmp path={path}".format(path=file_path))
        temp_file_path = file_path + '~'
        output_file = open(temp_file_path, 'wb')

        infile.seek(0)
        while True:
            data = infile.read(2<<16)
            if not data:
                break
            output_file.write(data)
        output_file.close()
        os.rename(temp_file_path, file_path)
        return file_path

    @classmethod
    def moveToDestination(cls,source,filename,subfolder=""):
        target = os.path.join(cls.savepath,subfolder,filename)
        l.debug("target filename:{target}".format(target=target))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))

        os.rename(source,target)
        return target



    @classmethod
    def deleteFile(cls,file):
        os.remove(file)

