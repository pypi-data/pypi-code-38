from mcvapi.masks.path_mask import PathMask as Class


class PathMask(Class):
    
    IMPORT = "from pythonvideoannotator_module_tracking.module_mcvapi.masks.path_mask import PathMask"
    


    def load(self, data, **kwargs):
        super(PathMask, self).load(data, **kwargs)
        datasets = data.get('pathmask_datasets', None)
        project  = data.get('project', kwargs.get('project', None))
        
        if not (datasets is None or project is None):
            paths = []
            for video_name, object2d_name, dataset_name in datasets:
                paths.append(project.find_video(video_name).find_object2d(object2d_name).find_dataset(dataset_name))
            self._param_pathmask_paths = paths


    def save(self, data, **kwargs):
        data = super(PathMask, self).save(data, **kwargs)
        datasets = self._param_pathmask_paths
        data['pathmask_datasets'] = [(dataset.object2d.video.name,dataset.object2d.name,dataset.name) for dataset in datasets]
        del data['pathmask_paths']
        return data