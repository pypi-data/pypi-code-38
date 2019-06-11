import sys, cv2
from pythonvideoannotator_models.models import Project

{imports}

class Pipeline({classes}): pass

if __name__=='__main__':

    p = Project()
    p.load( dict(), '{proj_path}' )

    VIDEOS = {inputdata}
    PARAMS = {parameters}

    for video_name in VIDEOS:
        video    = p.find_video(video_name)
        begin    = VIDEOS[video_name]['begin']
        end      = VIDEOS[video_name]['end']

        out_datasets = []
        for object2d_name, dataset_names in VIDEOS[video_name]['objects'].items():
            for dataset_name in dataset_names:
                dataset = video.find_object2d(object2d_name).find_dataset(dataset_name)
                if dataset is not None:
                    out_datasets.append(dataset)

        pipeline = Pipeline(**dict(PARAMS))
        capture  = cv2.VideoCapture(video.filepath)
        capture.set(cv2.CAP_PROP_POS_FRAMES, begin)
        
        firstblob_index = begin

        for index in range(begin, end):
            res, frame = capture.read()
            if not res: break

            res = pipeline.processflow(frame, frame_index=index)
            if firstblob_index==begin and len(res)>0: firstblob_index = index

        
        pipeline.end(
            res, 
            out_datasets=out_datasets,
            firstblob_index=firstblob_index,
            begin=begin,
            end=end
        )

    p.save()