import os
import fnmatch
import re
from swutil.validation import Float, Dict, List, Tuple, Bool, String, Integer
import os, sys, subprocess
def path_from_keywords(keywords,into='path'):
    '''
    turns keyword pairs into path or filename 
    
    if `into=='path'`, then keywords are separted by underscores, else keywords are used to create a directory hierarchy
    '''
    subdirs = []
    def prepare_string(s):
        s = str(s)
        s = re.sub('[][{},*"'+f"'{os.sep}]",'_',s)#replace characters that make bash life difficult by underscore 
        if into=='file':
            s = s.replace('_', ' ')#Remove underscore because they will be used as separator
        if ' ' in s:
            s = s.title()
            s = s.replace(' ','')
        return s
    if isinstance(keywords,set):
        keywords_list = sorted(keywords)
        for property in keywords_list:
            subdirs.append(prepare_string(property))
    else:
        keywords_list = sorted(keywords.items())
        for property,value in keywords_list:  # @reservedassignment
            if Bool.valid(value):
                subdirs.append(('' if value else ('not_' if into=='path' else 'not'))+prepare_string(property))
            #elif String.valid(value):
            #    subdirs.append(prepare_string(value))
            elif (Float|Integer).valid(value):
                subdirs.append('{}{}'.format(prepare_string(property),prepare_string(value)))
            else:
                subdirs.append('{}{}{}'.format(prepare_string(property),'_' if into == 'path' else '',prepare_string(value)))
    if into == 'path':
        out = os.path.join(*subdirs)
    else:
        out = '_'.join(subdirs)
    return out

def read_pdf(path,split_pages = False):
    import PyPDF2
    pdf_file = open(path, 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    n = read_pdf.getNumPages()
    outs=[]
    for i in range(n):
        page = read_pdf.getPage(i)
        page_content = page.extractText()
        outs.append(page_content)
    return outs if split_pages else '\n'.join(outs) 

def find_files(pattern, path=None,match_name=False):
    '''
    https://stackoverflow.com/questions/1724693/find-a-file-in-python

    WARNING: pattern is by default matched to entire path not to file names
    '''
    if not path:
        path = os.getcwd()
    result = []
    for root, __, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name if match_name else os.path.join(root,name),pattern):
                result.append(os.path.join(root, name))
    return result

def find_directories(pattern, path=None,match_name=False):
    '''
    WARNING: pattern is matched to entire path, not directory names, unless
    match_name = True
    '''
    if not path:
        path = os.getcwd()
    result = []
    for root, __, __ in os.walk(path):
        match_against = os.path.basename(root) if match_name else root
        try:
            does_match = pattern.match(match_against)
        except AttributeError:
            does_match = fnmatch.fnmatch(match_against,pattern)
        if does_match:
            result.append(root)
    return result

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

def zip_dir(zip_name, source_dir,rename_source_dir=False):
    '''
    https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    '''
    src_path = Path(source_dir).expanduser().resolve()
    with ZipFile(zip_name, 'w', ZIP_DEFLATED) as zf:
        for file in src_path.rglob('*'):
            path_in_zip = str(file.relative_to(src_path.parent))
            if rename_source_dir != False:
                _,tail = path_in_zip.split(os.sep,1)
                path_in_zip=os.sep.join([rename_source_dir,tail])
            zf.write(str(file.resolve()), path_in_zip)

def delete_empty_files(fpaths):  
    for fpath in fpaths:
        try:
            if os.path.isfile(fpath) and os.path.getsize(fpath) == 0:
                os.remove(fpath)
        except Exception:
            pass

def start_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def delete_empty_directories(dirs):
    for d in dirs:
        try:
            os.rmdir(d)
        except OSError: # raised if not empt
            pass
    

def append_text(file_name, text):
    if text:
        with open(file_name, 'a') as fp:
            fp.write(text)
