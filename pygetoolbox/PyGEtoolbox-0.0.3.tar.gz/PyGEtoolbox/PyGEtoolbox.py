import gzip
import numpy as np
import pandas as pd
import os 

# class for processing gene expression series from GEO

class Process_SOFT_format(object):

    def __init__(self, series):
        self.GE_data = series

        self.series_title = None
        self.series_summary = None
        self.series_samples = []
        self.series_overall_design = None
        self.platform = None
        self.series_geo_accession = None

        self.dataset = []
        self.gene_information = []
        self.sample_details = [] #details about samples - TODO

    def print_data(self):
        print(self.series_title)

        print(self.series_summary)

        print(self.series_samples)

        print(self.series_overall_design)

        print(self.platform)

        print(self.series_geo_accession)

    def save_samples(self, filename, dataset):
        folder = "../datasets/"
        test_path = folder + self.series_geo_accession
        path = folder + self.series_geo_accession + "/" + filename + ".pkl"

        if os.path.isdir(test_path):
            dataset.to_pickle(path)
        else:
            os.mkdir(test_path)
            dataset.to_pickle(path)

    def extract_metadata(self):  # extract metadata and list of samples
        counter = 0
        with gzip.open(self.GE_data) as lines:
            for line in lines:
                if line.startswith("!Series_title"):
                    self.series_title = line.split("=")[1].strip()
                elif line.startswith("!Series_summary"):
                    self.series_summary = line.split("=")[1].strip()
                elif line.startswith("!Series_overall_design"):
                    self.series_overall_design = line.split("=")[1].strip()
                elif line.startswith("^PLATFORM"):
                    self.platform = line.split("=")[1].strip()
                elif line.startswith("!Series_sample_id"):
                    self.series_samples.append(line.split("=")[1].strip())
                elif line.startswith("!Series_geo_accession"):
                    self.series_geo_accession = line.split("=")[1].strip()
                elif line.startswith("!Platform_data_row_count"):
                    break

    def get_samples(self):
        return self.series_samples

    def get_series_summary(self):
        return self.series_summary

    def extract_all_samples(self):  # extract all samples
        for i in range(len(self.series_samples)):
            sample = []
            with gzip.open(self.GE_data) as lines:

                for line in lines:
                    search_sample = "^SAMPLE = " + str(self.series_samples[i])
                    if line.startswith(search_sample):
                        print("Processing sample: ", self.series_samples[i])

                        for line2 in lines:
                            if line2.startswith("!sample_table_begin"):
                                cols_names = lines.next().rstrip().split("\t")
                                for line1 in lines:
                                    if line1.startswith("!sample_table_end"):
                                        break

                                    data = line1.rstrip().split("\t")
                                    sample.append(data)
                                break

            curr_dataset = pd.DataFrame(sample, columns=cols_names)
            self.dataset.append(curr_dataset)

            # saving the dataset
            self.save_samples(self.series_samples[i], curr_dataset)
            print("Successfully processed sample: ", self.series_samples[i])

    def extract_samples(self, samples):  # extract samples according to the user
        for i in range(len(samples)):
            sample = []
            with gzip.open(self.GE_data) as lines:

                for line in lines:
                    search_sample = "^SAMPLE = " + str(self.series_samples[i])
                    if line.startswith(search_sample):
                        print("Processing sample: ", self.series_samples[i])

                        for line2 in lines:
                            if line2.startswith("!sample_table_begin"):
                                cols_names = lines.next().rstrip().split("\t")
                                for line1 in lines:
                                    if line1.startswith("!sample_table_end"):
                                        break

                                    data = line1.rstrip().split("\t")
                                    sample.append(data)
                                break

            curr_dataset = pd.DataFrame(sample, columns=cols_names)
            self.dataset.append(curr_dataset)

            # saving the dataset
            self.save_samples(self.series_samples[i], curr_dataset)
            print("Successfully processed sample: ", self.series_samples[i])
    
    def get_dataset(self):
        return self.dataset

    def extract_sample_details(self, samples): 
        all_details = []
        for i in range(len(samples)):
            sample = []
            with gzip.open(self.GE_data) as lines:
                print "Processing sample: ", self.series_samples[i]
                for line in lines:
                    search_sample = "^SAMPLE = " + str(self.series_samples[i])
                    if line.startswith(search_sample):
                       
                        for line2 in lines:
                            if line2.startswith("!Sample_title"):
                                title = line2.split("=")[1].strip()
			    if line2.startswith("!Sample_source_name_ch1"):
				source_name = line2.split("=")[1].strip()
			    if line2.startswith("!Sample_characteristics_ch1"):
				characteristics = line2.split("=")[1].strip()	
			    if line2.startswith("!Sample_supplementary_file"):
				supplementary_file = line2.split("=")[1].strip()	
				sample_details = {'GEO_accession': self.series_samples[i], 'Title': title, 'Source_name': source_name, 'Characteristics': characteristics, 'Supplementary_file': supplementary_file}
				all_details.append(sample_details)
			    	break
				
    
        return all_details
    
    # extract gene title and symbol -
    def extract_gene_information(self):
        with gzip.open(self.GE_data) as lines:
            for line in lines:
                if line.startswith("!platform_table_begin"):
                    cols_names = lines.next().rstrip().split("\t")  # for future use
                    for line1 in lines:
                        if line1.startswith("!platform_table_end"):
                            break

                        data = line1.rstrip().split("\t")

                        if len(data) >= 11:
                            self.gene_information.append(
                                [data[0], data[9], data[10]])
                        else:
                            self.gene_information.append([data[0], None, None])
                    break

    def get_gene_information(self):
        return self.gene_information

    def affy_probe_set_ID_to_gene_id_and_description(self, probe_id):
        for x in self.gene_information:
            if probe_id == x[0]:
                return x[1], x[2]
        
    def add_gene_information_to_datasets(self, datasets):
        for i in range(len(datasets)):
            gene_title = []
            gene_symbol = []
            for j in range(len(self.gene_information)):
                gene_title.append(self.gene_information[j][1])
                gene_symbol.append(self.gene_information[j][2])

            # add data to dataframe
            datasets[i]['Gene title'] = gene_title
            datasets[i]['Gene symbol'] = gene_symbol

        return datasets
