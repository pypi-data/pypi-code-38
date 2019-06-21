"""Read private tags and add them to pydicom's datadict"""
import csv
import pydicom

def add_private_tags(path):
    """Add private tags from the given csv file, in the format:
    Tag,VR,Keyword,Description,VM
    0x111021b0,UN,UnknownProperty1,An unknown property,1
    """
    with open(path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            tag = pydicom.tag.Tag(row['Tag'])
            pydicom.datadict.add_dict_entry(tag, row['VR'], row['Keyword'],
                    row['Description'], row.get('VM', '1'))
