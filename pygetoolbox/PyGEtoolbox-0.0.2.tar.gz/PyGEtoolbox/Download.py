import gzip
import sys
import urllib2
from Functions import chunk_report, chunk_read

# class for downloading series (GSE) and datasets (GDS) from GEO


class Download(object):

    def download_SOFT_format(self, dataset, save_folder = "../SOFT_format/"):
        if "GSE" in dataset:
            identifier = dataset + "_family.soft.gz"
            url = "ftp://ftp.ncbi.nlm.nih.gov/geo/series/" + \
                dataset[:-3] + "nnn/" + dataset + "/soft/" + identifier
        elif "GDS" in dataset:
            identifier = dataset + "_full.soft.gz"
            url = "ftp://ftp.ncbi.nlm.nih.gov/geo/datasets/" + \
                dataset[:-3] + "nnn/" + dataset + "/soft/" + identifier
        else:
            print("Unknown dataset")
            sys.exit(1)

        save_folder = save_folder + identifier

        print("Retrieving data from GEO: ")

        try:
            response = urllib2.urlopen(url)
            data = chunk_read(response, report=chunk_report)
            save_ = open(save_folder, 'w')
            save_.write(data)
            save_.close()

            print("Successfully downloaded dataset: ", dataset)
        except Exception as e:
            print("Exception: ", e, " at ", url)
    
    def download_RAW_data(self, dataset, save_folder = "../RAW_data/"):
        identifier = "{}.tar".format(dataset)
        url = "https://www.ncbi.nlm.nih.gov/geo/download/?acc={}&format=file".format(dataset)
        
        save_folder = save_folder + identifier 

        print("Retrieving RAW data from GEO: ")

        try:
            response = urllib2.urlopen(url)
            data = chunk_read(response, report=chunk_report)
            save_ = open(save_folder, 'w')
            save_.write(data)
            save_.close()

            print("Successfully downloaded RAW data: ", dataset)
        except Exception as e:
            print("Exception: ", e, " at ", url)
            
    def download_CEL_file(self, sample, save_folder = "../cel_data/"):
        identifier = sample + ".CEL.gz"
        url = "ftp://ftp.ncbi.nlm.nih.gov/geo/samples/" + sample[:-3] + "nnn/" + sample + "/suppl/" + identifier
        
        save_folder = save_folder + identifier

        print("Retrieving CEL file from GEO: ")

        try:
            response = urllib2.urlopen(url)
            data = chunk_read(response, report=chunk_report)
            save_ = open(save_folder, 'w')
            save_.write(data)
            save_.close()

            print("Successfully downloaded CEL file: ", sample)
        except Exception as e:
            print("Exception: ", e, " at ", url)

    def download_CEL_file_from_URL(self, sample, url, save_folder = "../cel_data/"):
        identifier = sample + ".CEL.gz"
        
        save_folder = save_folder + identifier

        print("Retrieving CEL file from GEO: ")

        try:
            response = urllib2.urlopen(url)
            data = chunk_read(response, report=chunk_report)
            save_ = open(save_folder, 'w')
            save_.write(data)
            save_.close()

            print("Successfully downloaded CEL file: ", sample)
        except Exception as e:
            print("Exception: ", e, " at ", url)
