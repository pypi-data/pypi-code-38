import os
path_to_module = os.path.dirname(__file__)

datasets_path = os.path.join(path_to_module, "resources", "datasets")

BOOKS = os.path.join(datasets_path, "alice.txt")
SIMPSON = os.path.join(datasets_path, "simpson.txt")

# BOOKS = 'rnngen/resources/datasets/alice.txt'
# SIMPSON = 'rnngen/resources/datasets/simpson.txt'
# SIMPSON_SHORT = 'rnngen/resources/datasets/simpsonshort.txt'  defect, cannot be read by utf-8.

processed_data_path = os.path.join(path_to_module, "resources", "processeddata")

BOOKS_PROCESSED = os.path.join(processed_data_path, "alice_processed.txt")
SIMPSON_PROCESSED = os.path.join(processed_data_path, "simpson_processed.txt")
SIMPSON_SHORT_PROCESSED = os.path.join(processed_data_path, "simpson_short_processed.txt")


#BOOKS_PROCESSED = 'rnngen/resources/processeddata/alice_processed.txt'
#SIMPSON_PROCESSED = 'rnngen/resources/processeddata/simpson_processed.txt'
#SIMPSON_SHORT_PROCESSED = 'rnngen/resources/processeddata/simpson_short_processed.txt'
