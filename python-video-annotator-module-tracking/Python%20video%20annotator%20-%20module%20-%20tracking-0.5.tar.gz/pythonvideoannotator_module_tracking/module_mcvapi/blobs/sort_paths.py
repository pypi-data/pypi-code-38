from mcvapi.mcvbase import MCVBase
from mcvapi.blobs.order_by_position import combinations
import numpy as np, math, sys

from pyforms.basewidget import BaseWidget

class SortPaths(MCVBase):
    
    IMPORT = "from pythonvideoannotator_module_tracking.module_mcvapi.blobs.sort_paths import SortPaths"

    def __init__(self, **kwargs):
        super(SortPaths, self).__init__(**kwargs)
        self.load(kwargs)

    def load(self, data, **kwargs):
        super(SortPaths, self).load(data, **kwargs)
        self._param_sortpaths_paths = data.get('sortpaths_paths', [])

    def save(self, data, **kwargs):
        data = super(SortPaths, self).save(data, **kwargs)
        data['sortpaths_paths']  = self._param_sortpaths_paths
        return data

    def end(self, input_data, **kwargs):
        input_data       = super(SortPaths, self).end(input_data, **kwargs)
        progress_control = kwargs.get('progress_control', None)
        
        # tracked blobs paths
        blobs_paths = input_data 
        # the first frame index with blobs
        begin = kwargs.get('begin') 
        # the first frame index with blobs
        end   = kwargs.get('end') 
        # the first frame index with blobs
        firstblob_index      = kwargs.get('firstblob_index') 
        # datasets to fill in
        out_datasets  = kwargs.get('out_datasets')
        # datasets to use to sort the blobs paths
        datasets_list = self._param_pathmask_paths if hasattr(self, '_param_pathmask_paths') else out_datasets

        # Order paths and associate them to the right datasets
        if blobs_paths is not None:

            if progress_control:
                progress_control.label = 'Sorting paths'
                progress_control.value = 0
                progress_control.min   = 0
                progress_control.max   = len(blobs_paths)*len(datasets_list)*100

            # Make sure the number of datasets are the same of the blobs_paths. 
            # if the number of blobs paths are higher than the datasets then add None values to the list of datasets
            if len(blobs_paths)>len(datasets_list):
                datasets_list += [None for i in range(len(blobs_paths)-len(datasets_list))]
            elif len(blobs_paths)<len(datasets_list):
                # if the number of datasets are higher than the blobs paths then add None values to the list of blobs paths
                blobs_paths += [None for i in range(len(datasets_list)-len(blobs_paths))]

            # Compare the distances between each dataset and blobs_paths
            count = 0
            classifications = []
            for combination_index, combination in enumerate(combinations( blobs_paths, datasets_list)):
                classification = 0
                for pair_index, (blob_path, dataset) in enumerate(combination):
                    if not blob_path or not dataset:         continue
                    if len(dataset)==0 or len(blob_path)==0: continue
                    
                    distances = []
                    for i, p1 in enumerate(blob_path.path[:100]):
                        if p1 is None:  continue 
                        pos = dataset.get_position(firstblob_index + i)
                        if pos is None: continue 

                        p0   = pos
                        dist = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
                        
                        distances.append( dist )

                        # update the progress bar
                        if progress_control: progress_control.value = count; count+=1


                    classification += sum(distances)/len(distances) if len(distances)>0 else sys.maxsize
                    
                    # update the progress bar
                    if progress_control: progress_control.value = count = pair_index*combination_index*100
                
                classifications.append( (classification, combination) )
                
                # update the progress bar
                if progress_control: progress_control.value = count = len(combination)*combination_index*100

            classifications = sorted(classifications, key=lambda x: x[0])


            if len(classifications)>0:

                if progress_control:
                    progress_control.label = 'Updating datasets'
                    progress_control.value = 0
                    progress_control.min   = 0
                    progress_control.max   = (end-begin)*len(classifications[0][1])
                count = 0

                
                # add the empty values for first frames without detected objects
                for dataset in out_datasets:
                    for frame_index in range(begin, firstblob_index):
                        dataset.set_data_from_blob(frame_index, None)
                        if progress_control:
                            progress_control.value = frame_index
                            progress_control.value += 1

                # update the datasets
                for (blob_path, _), dataset in zip(classifications[0][1], out_datasets):
                    if dataset is None: continue
                    for frame_index in range(firstblob_index, end):
                        if progress_control: progress_control.value += 1
                        if blob_path is None:
                            dataset.set_data_from_blob(frame_index, None)
                        else:
                            if len(blob_path)<=(frame_index-firstblob_index): continue
                            blob = blob_path[frame_index-firstblob_index]
                            dataset.set_data_from_blob(frame_index, blob)

                           


        return out_datasets