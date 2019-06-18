################################
# Default
################################
import os,sys,json,random
import numpy as np
from PIL import Image as pImage, ImageDraw, ImageFont

real_path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
sys.path.append(real_path+"/lib/")

################################
# Engine
################################
import Utils as utils
from Image import Image

################################
# Mask R-CNN
################################
from lib import maskrcnn
################################
# Error
################################
class SupportFormatError(Exception):
    def _init_(self, format_):
        self.value = "SupportFormatError: Format '"+format_+"' is not supported."
    
    def _str_(self):
        return self.value   

################################
# Config
################################
class DefaultConfig:
    def __init__(self):
        self.MODEL_FILE_NAME = ""
        self.MODEL_PATH = ""
        self.VERSION = ""
        self.MEMO = ""
    
    def load_config(self, data):
        pass
    
    def save_config(self, path, file_name):
        pass

    def display(self):
        pass

    def get_value(self):
        pass

class MaskRCNNConfig(maskrcnn.config):
    def __init__(self):
        self.CATEGORY = ['BG']
        self.IMAGE_PATH = ""
        self.MODEL_FILE_NAME = ""
        self.MODEL_PATH = ""
        self.VERSION = ""
        self.MEMO = ""
        self.EPOCHS=1
        self.LAYERS="all"
        self.RESULT_TEST_NUM=100
        super().__init__()

    def _to_json_(self):
        """
            # _to_json_ : 설정 정보를 json 데이터로 반환합니다.
        """
        data = {}
        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                data[a] = getattr(self, a)
        return data

    def get_value(self, key):
        return getattr(self, key)

    def load_config(self, data):
        """
            # load_config : config 데이터를 json이나 경로를 입력하면 해당 정보에 맞게 데이터를 조정합니다.

            data : json 파일의 경로나, json 데이터를 받습니다.
        """
        assert data is not None or data != "", "load_config : data is None"
        config=None
        if isinstance(data, str):
            with open(data) as data_file:
                config = json.load(data_file)
        else:
            config = data
        keys = list(config.keys())

        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                if a in keys:
                    setattr(self,a,config[a])
        self.NUM_CLASSES = len(self.CATEGORY)
        self.RPN_ANCHOR_SCALES=tuple(self.RPN_ANCHOR_SCALES)
        self.MINI_MASK_SHAPE=tuple(self.MINI_MASK_SHAPE)
        self.MEAN_PIXEL=np.array(self.MEAN_PIXEL)
        super().__init__()
        del config
        del keys
    
    def set_config(self, option:str, value, re_setting=True):
        """
            # set_config : 특정 Key값의 데이터를 변경합니다.

            option : 변경하고자 하는 Key값을 입력합니다. 
            -------------------------------------
            value : 변경할 데이터를 입력합니다.
            -------------------------------------
            re_setting : 연관데이터를 갱신 할 것인지 여부입니다. 
        """
        setattr(self,option,value)
        if re_setting is True:
            super().__init__()

    def save_config(self, path:str, file_name:str):
        """
            # save_config : 설정 데이터를 json 파일 형태로 저장합니다.

            path : 저장할 경로를 입력합니다. 
            -------------------------------------
            file_name : 저장할 파일 명을 입력합니다. 
        """
        assert path is not None or path != "", "save_config : path is None"
        assert file_name is not None or file_name != "", "save_config : file_name is None"

        path = utils.create_folder(path)
        file_name = file_name.replace("."+file_name.split(".")[-1],"")
        path = path + file_name + ".json"
        data = self._to_json_()
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent='\t', sort_keys=True, default=utils.default_DICT_TO_JSON)
        del file_name
        del data
        return path

    def display(self):
        print(self._to_json_())

################################
# Dataset
################################
class DefaultDataset:
    def set_config(self, config):
        pass
    
    def add_data(self, data):
        # Add Data ( For Train)
        pass

class MaskRCNNDataset(maskrcnn.utils.Dataset):
    def set_config(self, config:MaskRCNNConfig):
        """
           # set_config : 설정 데이터를 셋팅합니다.
           
            config : 설정할 MaskRCNNConfig 데이터를 받습니다.
        """
        self._config_ = config 
        category = self._config_.CATEGORY[1:]
        for idx in range(1, len(category) + 1):
            self.add_class("deepGeo", idx, category[idx - 1])
        del category

    def add_data(self, data):
        """
            # add_data : 학습하거나 검증할 데이터를 넣습니다.

            data : json 파일명이나 list, stphoto, Image 데이터를 넣을 수 있습니다.
        """
        if isinstance(data, str) is True:
            if data.split(".")[-1] == 'json':
                uri = data
                data=None
                with open(uri) as data_file:    
                    data = json.load(data_file)
            else:
                data = json.loads(data)
        if isinstance(data, list) is True:
            for item in data:
                self.add_data(item)
        elif isinstance(data,dict):
            self._add_data_(Image(data['uri'],self._config_.IMAGE_PATH,data['annotations']))
        elif isinstance(data,Image):
            self._add_data_(data)
        else:
            raise SupportFormatError(type(data))

    def _add_data_(self, data:Image):
        """
            # _add_data_ : Image 데이터를 넣습니다.

            data : Image 타입을 받습니다. 
        """
        if isinstance(data, Image):
            self.add_image("deepGeo", image_id=len(self.image_info), path=data.get_path() + data.get_file_name(), image = data.to_stphoto())
            categories = self._config_.CATEGORY
            annotations = data.get_annotation()
            for annotation in annotations:
                if 'annotationText' in annotation:
                    text = annotation['annotationText']
                    if not(text in categories):
                        self.add_class("deepGeo", len(categories), text)
                        categories.append(text)
            self._config_.set_config("CATEGORY",categories)
        else:
            raise SupportFormatError(type(data))
    
    def load_mask(self, image_id):
        """
            # load_mask : Mask R-CNN에서 학습할 때 사용하는 Interface 함수 입니다.
        """
        info = self.image_info[image_id]
        image = info['image']
        annotations = image['annotations']
        width = image['width']
        height = image['height']
        mask = np.zeros([height, width, len(annotations)],dtype=np.uint8)
        class_ids = []
        idx=0
        for annotation in annotations:
            if 'areaInImage' in list(annotation.keys()):
                if 'annotationText' in list(annotation.keys()):
                    polygon = pImage.new('L',(width, height), 0)
                    area = annotation['areaInImage']
                    coordinates = area['coordinates']
                    if area['type'] in ['Rectangle', 'mbr']:
                        ImageDraw.Draw(polygon).rectangle(coordinates, fill=1)
                    elif area['type'] == 'Polygon':
                        if isinstance(coordinates[0], list)==False:
                            coordinates = [coordinates]
                        if len(coordinates[0])==2:
                            coordinates = [sum(coordinates, [])]
                        for coordinate in coordinates:
                            ImageDraw.Draw(polygon).polygon(coordinate, fill=1)
                    mask_ = np.array(polygon)
                    for i in range(height):
                        for j in range(width):
                            mask[i][j][idx]=mask_[i][j]
                    idx+=1
                    class_ids.append(self._config_.CATEGORY.index(annotation['annotationText']))
                    del mask_
                    del area
                    del coordinates
                    del polygon
        del width
        del height
        del annotations
        del info
        del image
        return mask, np.array(class_ids)

    def image_reference(self, image_id):
        """
            # image_reference : Mask R-CNN에서 학습할 때 사용하는 Interface 함수 입니다.
        """
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "deepGeo":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)
    
################################
# Model
################################
        
class DefaultModel:
    def __init__(self, config):
        pass

    def get_config(self):
        pass

    def create_dataset(self, name):
        pass

    def add_dataset(self, name, dataset):
        pass

    def delete_dataset(self, name):
        pass

    def add_data(self, name, data):
        pass

    def validation(self, validation_dataset_name, weight:str=None):
        pass

    def train(self, train_dataset_name, validation_dataset_name, weight:str=None):
        pass

    def detect(self, data, option):
        pass

class MaskRCNNModel:
    FIRST_POLYGON_DATA = 1
    FIRST_BBOX_DATA = 2
    FIRST_BBOX_DATA_WITH_SAVE = 3
    FIRST_POLYGON_DATA_WITH_SAVE = 4
    _OPTION_ = [FIRST_POLYGON_DATA,FIRST_BBOX_DATA,FIRST_BBOX_DATA_WITH_SAVE,FIRST_POLYGON_DATA_WITH_SAVE]
    def __init__(self, config:MaskRCNNConfig):
        """
            # __init__ : MaskRCNNModel를 생성하고 설정파일로 설정합니다.

            config : MaskRCNNConfig 타입만 받습니다.
        """
        assert config is not None, "__init__ : config is None"
        self._config_ = config
        self._dataset_={}
        self._model_path_ = utils.create_folder(self._config_.MODEL_PATH.split(self._config_.MODEL_FILE_NAME)[0])
        self._model_ = [None, "training"]
    
    def _get_model_(self, name, mode):
        """
            # _get_model_ : 모델 데이터를 메모리에 올립니다.

            name : 모델 데이터의 위치와 파일명이 들어 있는 경로, 혹은 last , None 데이터를 받습니다.
            if name is "last" : 마지막으로 학습된 데이터를 가져옵니다.
            if name is None : 기본 모델 데이터를 가져옵니다.
            if name is path : 해당 파일을 읽어옵니다.
            -------------------------------------
            mode : 학습인지 분석인지 선택합니다.
            if mode is "inference" : 분석 모드로 모델을 설정합니다.
            if mode is "training" : 학습 모드로 모델을 설정합니다.
        """
        if self._model_[0] is not None and self._model_[1] == mode:
            return self._model_[0]
        if mode == "training":
            self._config_.set_config("IMAGES_PER_GPU",1)
        model = maskrcnn.model.MaskRCNN(mode=mode, config=self._config_, model_dir=self._model_path_)
        if name is None:
            name = model.get_imagenet_weights()
        elif name == "last":
            name = model.find_last()[1]
        assert name != "", "Provide path to trained weights"
        print("Loading weights from ", name)
        model.load_weights(name, by_name =True)
        self._model_[0] = model
        self._model_[1] = mode
        return self._model_[0]

    def get_config(self):
        """
            # get_config : 설정 데이터를 반환합니다.
        """
        return self._config_

    def create_dataset(self, name):
        """
            # create_dataset : 데이터셋을 생성합니다.
            
            name : 생성할 데이터셋의 이름을 지정합니다. 중복시 이전 것은 제거 됩니다.
        """
        dataset = MaskRCNNDataset()
        dataset.set_config(self._config_)
        self._dataset_.update({name:dataset})

    def get_dataset(self, name):
        """
            # get_dataset : 데이터셋을 가져옵니다.

            name : 데이터셋의 이름입니다.
        """
        if name in list(self._dataset_.keys()):
            return self._dataset_[name]
        return None

    def add_dataset(self, name, dataset:MaskRCNNDataset):
        """
            # add_dataset : 외부 데이터 셋을 추가합니다.

            name : 데이터셋의 이름을 지정합니다. 중복시 이전 것은 제거 됩니다.
            -------------------------------------
            dataset : MaskRCNNDataset 타입의 객체만 받습니다.
        """
        self._dataset_.update({name:dataset})

    def delete_dataset(self, name):
        del self._dataset_[name]

    def add_data(self, name, data):
        """
            # add_data : 학습할 데이터를 추가합니다.

            name : 추가할 데이터셋 이름을 입력합니다.
            -------------------------------------
            data : 데이터를 추가합니다.
        """
        self._dataset_[name].add_data(data)

    def validation(self, validation_dataset_name, weight:str):
        """
            # validation : 검증을 진행합니다.

            validation_dataset_name : 검증으로 사용할 데이터셋의 이름을 입력합니다.
            -------------------------------------
            weight : 사용할 가중치 정보를 입력합니다. (last, None, path+model_name)
        """
        model = self._get_model_(weight,"inference")
        dataset_val = self._dataset_[validation_dataset_name]
        dataset_val.prepare()

        image_ids = np.random.choice(dataset_val.image_ids, self._config_.RESULT_TEST_NUM)
        APs = []
        for image_id in image_ids:
            # Load image and ground truth data
            image, _, gt_bbox, _ = \
                maskrcnn.model.load_image_gt(dataset_val, self._config_,
                                    image_id, use_mini_mask=True)
            _ = np.expand_dims(maskrcnn.model.mold_image(image, self._config_), 0)
            # Run object detection
            results = model.detect([image], verbose=0)
            r = results[0]
            # Compute AP
            AP, _, _, _ = \
                maskrcnn.utils.compute_ap(gt_bbox[:, :4], gt_bbox[:, 4],
                                r["rois"], r["class_ids"], r["scores"])
            APs.append(AP)
        print("mAP: ", np.mean(APs))

    def train(self, train_dataset_name, validation_dataset_name, weight:str=None):
        """
            # train : 학습을 진행합니다.

            train_dataset_name : 학습할 데이터셋의 이름을 입력합니다.
            -------------------------------------
            validation_dataset_name : 검증으로 사용할 데이터셋의 이름을 입력합니다.
            -------------------------------------
            weight : 사용할 가중치 정보를 입력합니다. (last, None, path+model_name)
        """
        model = self._get_model_(weight,"training")

         # 학습할 데이터 셋
        dataset_train = self._dataset_[train_dataset_name]
        dataset_train.prepare()

        # 점검할 데이터 셋
        dataset_val = self._dataset_[validation_dataset_name]
        dataset_val.prepare()
        
        print("학습 시작")
        model.train(dataset_train, dataset_val,learning_rate=self._config_.LEARNING_RATE,
                        epochs=self._config_.EPOCHS,layers=self._config_.LAYERS)

        print("학습 완료")
        model_path = model.find_last()[1]
        del model
        del dataset_train
        del dataset_val
        model_path = model_path.replace("\\","/")
        self._config_.MODEL_FILE_NAME = model_path.split("/")[-1]
        self._config_.MODEL_PATH = model_path.split(self._config_.MODEL_FILE_NAME)[0]
        return model_path

    def detect(self, data, option=1):
        """
            # detect : 데이터 분석을 진행합니다.
            
            data : 분석할 데이터를 받습니다. Image 및 ndarray 만 받습니다.
            -------------------------------------
            option : 예측할 때 조건을 제시합니다.
                FIRST_BBOX_DATA_WITH_SAVE : BBOX를 우선으로 저장을 합니다.
                FIRST_POLYGON_DATA_WITH_SAVE : POLYGON를 우선으로 저장합니다.
        """
        assert isinstance(data, Image) or isinstance(data, np.ndarray), "Model -> detect -> 지원하지 않은 포맷입니다."
        assert option in MaskRCNNModel._OPTION_  or option is None, "Model -> detect -> 지원하지 않은 옵션입니다."

        model_path  = utils.create_folder(self._config_.MODEL_PATH)
        model = self._get_model_(model_path+self._config_.MODEL_FILE_NAME,"inference")

        if isinstance(data, Image):
            numpy_array = [data.to_numpy()]
        else:
            numpy_array = [data]

        result = model.detect(numpy_array, verbose=0)

        if isinstance(data, np.ndarray):
            return result

        points = None

        issave = False
        if option in [MaskRCNNModel.FIRST_BBOX_DATA_WITH_SAVE, MaskRCNNModel.FIRST_POLYGON_DATA_WITH_SAVE]:
            issave=True
        img = result[0]
        annotations = []
        
        if option == MaskRCNNModel.FIRST_BBOX_DATA:
            points = img['rois'].tolist()
            option = "bbox"
        else:
            points = utils.np_to_polygon(img["masks"])
            option = "polygon"
            
        cnt_ids = len(img['class_ids'])
        for idx in range(cnt_ids):
            try:
                annotation ={
                    "areaInImage":{
                        "type": option,
                        "coordinates":points[idx],
                        "score":float(img['scores'][idx])
                    },
                    "annotationText":self._config_.CATEGORY[img['class_ids'][idx]]
                }
                annotations.append(annotation)
            except Exception as e:
                print(idx, " - pass! - ", e)
        data.add_annotation(annotations)
        if issave is True:
            info = data.to_stphoto()
            data.draw_annotations(info['annotations'],option="PolygonAndRectangleTextWithBackground")
            data.save(self._config_.IMAGE_PATH, image_name=None, image_format="png")
        del model_path
        del numpy_array
        del points
        del issave
        del annotations
        return data