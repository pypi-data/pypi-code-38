from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile,io, re
##            try:
##                xml_content = document.read('word/header1.xml')
##          except:
##                xml_content = document.read('word/document.xml')
name = "docuscan"
class DocuScan():
    '''
        Class that scans documents (pdf, doc and docx) and returns their strings,
        as well as can execute regular expressions.
    '''
    def __init__(self,fileName):
        self.filePathName=fileName
        self.fileName=fileName.rsplit('/', 1)[-1]
        self.fileFormat=fileName.rsplit('.',1)[-1]

    def returnFileText(self):
        '''
        Returns the file's text in a large string
        Usage:
            returnFileText()
        Returns:
            'Lorem ipsum ....'
        '''
        if self.fileFormat == 'pdf':
            fp = open(self.filePathName, 'rb')
            rsrcmgr = PDFResourceManager()
            retstr = io.StringIO()
            codec = 'utf-8'
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
                file =  retstr.getvalue()

        elif self.fileFormat=='doc':
            file=open(file,encoding='latin-1').read()

        elif self.fileFormat=='docx':
            WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            PARA = WORD_NAMESPACE + 'p'
            TEXT = WORD_NAMESPACE + 't'
            """
            Take the path of a docx file as argument, return the text in unicode.
            """
            document = zipfile.ZipFile(self.filePathName)
            xml_content = document.read('word/document.xml')
            document.close()
            try:
                tree = XML(xml_content)
                paragraphs = []
                for paragraph in tree.getiterator(PARA):
                    texts = [node.text
                            for node in paragraph.getiterator(TEXT)
                            if node.text]
                    if texts:
                        paragraphs.append(''.join(texts))
            except:
                return Exception
            file='\n\n'.join(paragraphs)

        return file

    
    def executeRegex(self, regularExpression):
        '''
            Executes specified regular expression on any given document that is a doc, docx or pdf.
            Usage:
                executeRegex('regularexpression')
            Returns:
                listOfElements-satisfied-by-regex
        '''
        fileText = self.returnFileText()
        listOfRegex = re.findall(regularExpression, fileText)
        return listOfRegex



