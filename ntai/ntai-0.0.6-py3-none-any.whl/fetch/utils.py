import urllib.parse, requests, os, gzip, shutil


HG_TABLES_URL = 'http://genome.ucsc.edu/cgi-bin/hgTables'

HG_DOWNLOAD_DIRECTORY_URL = 'http://hgdownload.soe.ucsc.edu'

HG38_DOWNLOAD_DIRECTORY_URL = '{}/goldenPath/hg38/bigZips'.format(HG_DOWNLOAD_DIRECTORY_URL)

HG38_FASTA_URL = '{}/hg38.fa.gz'.format(HG38_DOWNLOAD_DIRECTORY_URL)
HG38_CHROM_SIZES_URL = '{}/hg38.chrom.sizes'.format(HG38_DOWNLOAD_DIRECTORY_URL)



DEFAULT_PARAMS = {
    'ignoreCookie': 1,
    'hgta_track': 'wgEncodeGencodeCompV28',
    'boolshad.hgta_printCustomTrackHeaders':0,
    'hgta_ctName':'tb_wgEncodeGencodeCompV28',
    'hgta_ctDesc': 'table+browser+query+on+wgEncodeGencodeCompV28',
    'hgta_ctVis': 'pack',
    'hgta_ctUrl': None,
    'fbUpBases': 200,
    'fbQual': 'exon',
    'fbExonBases': 0,
    'fbIntronBases': 0,
    'fbDownBases': 200,
    'hgta_doGetBed': 'get+BED'
}


def fname(file:str, directory:str=None):
    '''
    Notes:
        1. if directory is None and file is just the basename, directory is set
            to '~/Downloads'
        2. if file is the full path and directory is set to none, directory is
            ignored.
        3. if file is partial path and directory is not none, directory is
            prepended to the file.
    Arguments:
        file (str): the file's name, either basename or full path.
        directory (str): the directory of the file. Default is None.
    Returns:
        fullpath (str): full path of the file given the directory

    '''
    # user passes just the filename. Then defaults to download directory
    if directory is None and os.path.basename(file) == file:
        directory = '~/Downloads'

    if directory is None:
        directory = ''

    name = os.path.expanduser(os.path.join(directory, file))
    return name




def fetch_exons(
    file:str='encode_gencode_comp_v28_exons.bed',
    directory:str=None
):
    params = {'fbQual': 'exon'}
    request = requests.get(HG_TABLES_URL, params={**DEFAULT_PARAMS, **params})
    if request.status_code == 200:
        with open(fname(file, directory), 'w') as f:
            f.write(request.text)

def fetch_introns(
    file:str='encode_gencode_comp_v28_introns.bed',
    directory:str=None
):
    params = {'fbQual': 'intron'}
    request = requests.get(HG_TABLES_URL, params={**DEFAULT_PARAMS, **params})
    if request.status_code == 200:
        with open(fname(file, directory), 'w') as f:
            f.write(request.text)

def fetch_hg38_chrom_sizes(
    file:str='hg38.chrom.sizes',
    directory:str=None
):
    request = requests.get(HG38_CHROM_SIZES_URL)
    if request.status_code == 200:
        with open(fname(file, directory), 'w') as f:
            f.write(request.text)

def fetch_hg38(
    file:str="hg38.fa.gz",
    directory:str=None
):
    request = requests.get(HG38_FASTA_URL)
    if request.status_code == 200:
        with open(fname(file, directory), 'wb') as f:
            f.write(request.raw.read())

def decompress(path:str, odir:str=None):
    '''
    Decompresses the .gz file specified by path. Decompressed file keeps the
    same basename e.g. my_file.txt.gz --> my_file.txt

    Arguments:
        path (str): full path to a .gz compressed file
        odir (str): optional. A new output directory for the file. By default None.

    Returns:
        None.
    '''
    ofile = os.path.splitext(os.path.expanduser(path))[0]
    if odir is not None:
        ofile = os.path.join(odir, os.path.basename(ofile))
    with gzip.open(path, 'rb') as f_in:
        with open(ofile, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def fetch_files(directory:str):
    fetch_exons(directory=directory)
    fetch_introns(directory=directory)
    fetch_hg38_chrom_sizes(directory=directory)
    fetch_hg38(directory=directory)
    decompress(os.path.join(directory, 'hg38.fa.gz'))
