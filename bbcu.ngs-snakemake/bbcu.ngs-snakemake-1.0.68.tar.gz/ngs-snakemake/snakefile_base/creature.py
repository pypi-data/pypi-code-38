# send to args list of requested parameters, one or more of the following:
# RUN_NGSPLOT, NGSPLOT_GENOME, INTERMINE_WEB_QUERY, INTERMINE_WEB_BASE, MINE_CREATURE, ANNOTAT_TYPE, GENE_DB_URL, RUN_NGSPLOT, MACS_GENOME_SIZE
#creature=name of creature, ngs_plot_exe=True/False

def get_creature_parameters(creature, ngs_plot_exe, *args):
    NGSPLOT_GENOME = 'hg19'
    INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
    INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
    MINE_CREATURE = 'H. sapiens'
    ANNOTAT_TYPE = 'RefSeq'
    GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
    RUN_NGSPLOT = False
    MACS_GENOME_SIZE = 'hs'

    if creature == 'hg38':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'hg38-gencode':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'Gencode'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'hg19':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'hg19-genecode':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'Genecode'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'mm10':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'mm10'
        INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'M. musculus'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.mousemine.org\/mousemine\/keywordSearchResults.do?searchTerm="
        MACS_GENOME_SIZE = 'mm'
    elif creature == 'mm10-gencode':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'mm10'
        INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'M. musculus'
        ANNOTAT_TYPE = 'Gencode'
        GENE_DB_URL = "http:\/\/www.mousemine.org\/mousemine\/keywordSearchResults.do?searchTerm="
        MACS_GENOME_SIZE = 'mm'
    elif creature == 'mm10hg19':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'M. musculus'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 1870000000 + 1000000000 #Mouse + Human
    elif creature == 'mm10hg19-gencode':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'M. musculus'
        ANNOTAT_TYPE = 'Gencode'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = '' #Not work for now. 1870000000 + 1000000000 #Mouse + Human
    elif creature == 'mm10hg38':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'M. musculus'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = '' #Not work for now. 1870000000 + 1000000000 #Mouse + Human
    elif creature == 'mm10hg38-gencode':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'http:\/\/www.mousemine.org\/mousemine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'M. musculus'
        ANNOTAT_TYPE = 'Gencode'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = '' #Not work for now. 1870000000 + 1000000000 #Mouse + Human
    if creature == 'hg38+tb40+sv40':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'hg38+tb40+sv40-gencode':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'Gencode'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'hg19+tb40+sv40':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'hg19+tb40+sv40-genecode':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'Genecode'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 'hs'
    elif creature == 'tair10' or creature == 'tair11-araport':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'https:\/\/apps.araport.org\/thalemine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'A. thaliana'
        ANNOTAT_TYPE = 'Araport'
        GENE_DB_URL = "https:\/\/www.arabidopsis.org\/servlets\/Search?type=general\&search_action=detail\&method=1\&show_obsolete=F\&sub_type=gene\&SEARCH_EXACT=4\&SEARCH_CONTAINS=1\&name="
        MACS_GENOME_SIZE = '' #Not work for now. 116000000 # According to https://www.nature.com/articles/35048692
    elif creature == 'sl3':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'https:\/\/phytozome.jgi.doe.gov\/phytomine'
        INTERMINE_WEB_BASE = 'https:\/\/phytozome.jgi.doe.gov'
        MINE_CREATURE = 'S. lycopersicum'
        ANNOTAT_TYPE = 'Sol genomics'
        GENE_DB_URL = "https:\/\/phytozome.jgi.doe.gov\/phytomine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = '' #Not work for now. 950000000 # According to https://solgenomics.net/organism/1/view/
    elif creature == 'emihu1':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = ''
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = ''
        ANNOTAT_TYPE = 'emiliania_huxleyi'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = 167675649 # According to https://www.ebi.ac.uk/ena/data/view/GCA_000372725.1
    elif creature == 'danRer10':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'Zv9'
        INTERMINE_WEB_QUERY = 'http:\/\/www.zebrafishmine.org'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'D. rerio'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.zebrafishmine.org\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = ''
    elif creature == 'barley_cv_morex-HighConfidence' or creature == 'barley_cv_morex-LowConfidence':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'https:\/\/phytozome.jgi.doe.gov\/phytomine'
        INTERMINE_WEB_BASE = 'https:\/\/phytozome.jgi.doe.gov'
        MINE_CREATURE = 'H. vulgare early-release'
        ANNOTAT_TYPE = 'doi:10.5447\/IPK\/2016\/38'
        GENE_DB_URL = "https:\/\/phytozome.jgi.doe.gov\/phytomine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = ''
    elif creature == 'barley_cv_morex-LowConfidence':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'https:\/\/phytozome.jgi.doe.gov\/phytomine'
        INTERMINE_WEB_BASE = 'https:\/\/phytozome.jgi.doe.gov'
        MINE_CREATURE = 'H. vulgare early-release'
        ANNOTAT_TYPE = 'doi:10.5447\/IPK\/2016\/46'
        GENE_DB_URL = "https:\/\/phytozome.jgi.doe.gov\/phytomine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = ''
    elif creature == 'rn6' or creature == 'rn6-HornsteinLab':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'http:\/\/ratmine.mcw.edu\/ratmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'R. norvegicus'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/ratmine.mcw.edu\/ratmine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = ''
    elif creature == 'ASM15095v2':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = ''
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = ''
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "https:\/\/www.ncbi.nlm.nih.gov\/nuccore\/"
        MACS_GENOME_SIZE = ''
    elif creature == 'ASM361127v1':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = ''
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = ''
        ANNOTAT_TYPE = 'NCBI'
        GENE_DB_URL = "https:\/\/www.ncbi.nlm.nih.gov\/nuccore\/"
        MACS_GENOME_SIZE = ''
    elif creature == 'dm6':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = 'dm6'
        INTERMINE_WEB_QUERY = 'http:\/\/www.flymine.org\/flymine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'D. melanogaster'
        ANNOTAT_TYPE = 'RefSeq'
        GENE_DB_URL = "http:\/\/www.flymine.org\/flymine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = ''
    elif creature == 'Oeuropaea_451_v1':
        RUN_NGSPLOT = True
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = ''
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        INTERMINE_WEB_QUERY = 'https:\/\/phytozome.jgi.doe.gov\/phytomine'
        INTERMINE_WEB_BASE = 'https:\/\/phytozome.jgi.doe.gov'
        MINE_CREATURE = 'O. europaea early-release'
        ANNOTAT_TYPE = 'Phytozome'
        GENE_DB_URL = "https:\/\/phytozome.jgi.doe.gov\/phytomine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = ''
    elif creature == 'WBcel235':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''
        INTERMINE_WEB_QUERY = 'http:\/\/intermine.wormbase.org\/tools\/wormmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'C. elegans'
        ANNOTAT_TYPE = 'Ensembl'
        GENE_DB_URL = "http:\/\/intermine.wormbase.org\/tools\/wormmine\/keywordSearchResults.do?searchSubmit=GO\&searchTerm="
        MACS_GENOME_SIZE = ''
    elif creature == 'toy':
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = 'hg19'
        INTERMINE_WEB_QUERY = 'http:\/\/www.humanmine.org\/humanmine'
        INTERMINE_WEB_BASE = INTERMINE_WEB_QUERY
        MINE_CREATURE = 'H. sapiens'
        ANNOTAT_TYPE = 'Gencode'
        GENE_DB_URL = "http:\/\/www.genecards.org\/cgi-bin\/carddisp.pl?gene="
        MACS_GENOME_SIZE = ''

    if not ngs_plot_exe:  # empty string ''
        RUN_NGSPLOT = False
        NGSPLOT_GENOME = ''

    returned_values = []
    for arg in args:
        returned_values.append(eval(arg))

    return returned_values

