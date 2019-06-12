import h5py
import os

class HDF5DatasetWriter:
    def __init__(self, data_dims, label_dims, label_type, outputPath, dataKey="images", bufSize=1000):
        if os.path.exists(outputPath):
            raise ValueError("The supplied ‘outputPath‘ already exists and cannot be overwritten. Manually delete the file before continuing.", outputPath)
        self.db = h5py.File(outputPath, "w")
        self.data = self.db.create_dataset(dataKey, data_dims, dtype="float")
        self.labels = self.db.create_dataset("labels", label_dims, dtype=label_type)
        self.len_labels = self.db.create_dataset("len_labels", (label_dims[0],), dtype=label_type)
        self.bufSize = bufSize
        self.buffer = {"data": [], "labels": []}
        self.idx = 0
    
    def add(self, rows, labels, lens):
        self.buffer["data"].extend(rows)
        self.buffer["labels"].extend(labels)
        self.buffer["len_labels"].extend(lens)
        if len(self.buffer["data"]) >= self.bufSize:
            self.flush()

    def flush(self):
        i = self.idx + len(self.buffer["data"])
        self.data[self.idx:i] = self.buffer["data"]
        self.labels[self.idx:i] = self.buffer["labels"]
        self.len_labels[self.idx:i] = self.buffer["len_labels"]
        self.idx = i
        self.buffer = {"data": [], "labels": [], "len_labels": []}
    
    def storeClassLabels(self, classLabels):
        dt = h5py.special_dtype(vlen=str)
        labelSet = self.db.create_dataset("label_names", (len(classLabels),), dtype=dt)
        labelSet[:] = classLabels
    
    def close(self):
        if len(self.buffer["data"]) > 0:
            self.flush()
        self.db.close()