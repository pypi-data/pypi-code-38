import os
import numpy as np
import exifread
import piexif
import json
from PIL import Image as pImage, ImageDraw, ImageFont
import Utils as utils


class SupportFormatError(Exception):
    def _init_(self, format_):
        self.value = "SupportFormatError: Format '"+format_+"' is not supported."
    
    def _str_(self):
        return self.value

class ImageLoadError(Exception):
    def _init_(self, image_name):
        self.value = "ImageLoadError: Unable to retrieve '"+image_name+"' file."
    
    def _str_(self):
        return self.value

class FontLoadError(Exception):
    def _init_(self, font_name):
        self.value = "The font file does not exist. (/fonts/"+font_name+".ttf)"
    
    def _str_(self):
        return self.value

class FontUnitError(Exception):
    def _init_(self, font_size):
        self.value = "Unit of font size not supported. ("+font_size+")"
    
    def _str_(self):
        return self.value

class Image:
    version = 1.1904291722
    """
    UPDATE

    Ver 1.1905081530
        - draw_annotation 함수 수정
            - 소문자 폴리곤도 적용

    Ver 1.1905061224
        - 함수 추가
            - display = STPhoto 양식으로 화면에 출력

    Ver 1.1904301337
        - 함수 로직 수정
            - _extract_exif_ = Exif 데이터 손상시 처리

    Ver 1.1904291722
        - 주석 정리
        - 함수 생성 및 수정, 작동 확인
            - get_path = 이미지의 경로를 가져옵니다. (로컬)
            - get_file_name = 이미지의 파일 이름을 가져옵니다. (로컬)
            - set_annotation = annotation 데이터를 입력합니다.
            - get_annotation = annotation 데이터를 가져옵니다.
            - to_stphoto = 이미지를 STPhoto 포맷으로 반환합니다.
            - get_size = 이미지의 크기 가져옵니다.
            - get_info = 함수 수정 get_size 적용
    Ver 1.1904282027
        - 함수 생성 및 작동 확인
            - _open_ = 이미지 열기
            - _get_image_ = 내부적으로 이미지를 가져옵니다.
            - _extract_bexif_ = 바이너리로 exif 데이터를 추출합니다.
            - _extract_exif_ = 딕셔너리 형태로 exif 데이터를 추출합니다.
            - _get_font_ = 폰트를 설정합니다.
            - _draw_annotation_ = STPhoto 기준으로 데이터를 그립니다.
            - create_thumbnail = 썸네일을 생성합니다.
            - save = 설정된 정보를 바탕으로 이미지를 저장합니다.
            - delete = 원본 이미지를 제거합니다.
            - get_info = 이미지에 대한 정보를 딕셔너리 형태로 받습니다.
            - get_location = 이미지의 EXIF 정보를 가져옵니다.
            - get_altitude = 이미지의 EXIF 정보를 가져옵니다.
            - get_datetime = 이미지의 EXIF 정보를 가져옵니다.
            - get_direction = 이미지의 EXIF 정보를 가져옵니다.
            - get_distance = 이미지의 EXIF 정보를 가져옵니다.
            - to_numpy = 이미지 데이터를 Numpy 형태로 반환합니다.
            - draw_annotations = 이미지를 STPhoto 데이터 바탕으로 그립니다.
            - to_gray_numpy = 이미지를 그레이스케일 형태의 Numpy 데이터로 받습니다.
        - 이미지 오픈시 Orientation 기준으로 회전 후 EXIF 수정하여 저장
        - ERROR 형태 구현 및 작동 확인
            - SupportFormatError = 지원하지 않은 저장 포맷일 경우 발생
            - ImageLoadError = 이미지 파일이 없을 경우 발생
            - FontLoadError = 폰트가 존재하지 않을 경우 발생
            - FontUnitError = 지원하지 않은 타입의 폰트 크기를 기입시 발생
    Ver 1.1906171535
        - EXIF 데이터 추출 오류 해결
            - get_altitude
            - get_direction
            - get_distance
        
    """

    def __init__(self, uri, image_path, annotations = None):
        self._uri_=uri
        self._path_ = utils.create_folder(image_path)
        self._file_name_ = utils.download_image(uri, image_path)
        self._image_ = None
        self._exif_ = self._extract_exif_()
        if annotations is None:
            annotations = []
        self._annotation_ = annotations
        if "Image Orientation" in (self._exif_.keys()):
            self.save(self._path_, image=utils.image_rotation(self._open_(), self._exif_['Image Orientation']))
    
    def __str__(self):
        return self.to_stphoto_as_json()

    def _open_(self):
        """
            # _open_ : 이미지 파일로 부터 Pillow Object 생성합니다.
        """
        return pImage.open(self._path_ + self._file_name_).convert('RGB')

    def _get_image_(self, image=None, is_new=False):
        """
            # _get_image_ : 이미지를 가져옵니다.

            is_new : 이미지를 새로 가져올 것인지 물어봅니다.
        """
        if image is not None:
            return image
        image = self._image_
        if is_new is True:
            image = self._open_()
        elif image is None:
            self._image_ = self._open_()
            image = self._image_
        else:
            return self._image_
        if image is None:
            raise ImageLoadError(self._file_name_)
        else:
            return image

    def _extract_bexif_(self, image=None):
        """
            # _extract_bexif_ : EXIF 데이터를 바이너리로 변환합니다.
            image : 바이너리를 추출할 Pillow Object 입니다.

            image is None : 기본 객체입니다.
            image is Pillow Object : Pillow Object 저장합니다.
        """
        image = self._get_image_(image,True)
        try:
            exif_dict = piexif.load(image.info["exif"])
            exif_dict["0th"][piexif.ImageIFD.Orientation] = [1]
            exif_bytes = piexif.dump(exif_dict)
        except Exception:
            exif_bytes = None
        return exif_bytes

    def _extract_exif_(self):
        """
            # _extract_exif_ : EXIF 데이터를 딕셔너리화 합니다.
        """
        try:
            with open(self._path_ + self._file_name_, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            return tags      
        except IndexError:
            return {}

    def _get_font_(self, font_name, font_size=0):
        """
            # _get_font_ : annotation 에서 텍스트를 그릴때 필요한 폰트 및 폰트 크기를 설정 및 가져온다.
            
            font_size : 폰트의 크기를 지정한다.

            0 : 폰트의 크기를 이미지 크기에 맞게 비례하여 지정한다.
            1 이상 : 해당 크기에 맞게 표시한다.
            -------------------------------------
            font_name : 폰트를 지정한다. (/fonts/ 위치에 ttf 형태의 파일을 넣으면 사용 가능하다.)
            font_name is "TmonMonsori" : 티몬의 몬소리 체를 사용한다. (/fonts/TmonMonsori.ttf)
        """
        font_path = os.path.dirname(os.path.realpath(__file__)).replace("\\","/") +"/fonts/"+font_name+".ttf"
        if os.path.isfile(font_path) is False:
            raise FontLoadError(font_name)
        if isinstance(font_size,int) == False:
            raise FontUnitError(font_size)
        if font_size <= 0 :
            y, _, _ = self.to_numpy().shape
            font_size =int(y*5/240)
        return ImageFont.truetype(font_path, font_size), font_size

    def _draw_annotation_(self, draw_image, annotation, color, opacity=0.5,option="", font='TmonMonsori',font_size=0):
        """
            # _draw_annotation_ : 화면에 STPhoto 양식으로 그린다.

            draw_image : Pillow의 Draw_Image 타입의 데이터를 받는다.
            -------------------------------------
            annotation : STPhoto 타입의 annotations의 annotation의 데이터를 받는다.
            -------------------------------------
            color : RGB 형태의 데이터를 받는다. 
            -------------------------------------
            opacity : 객체를 식별할 폴리곤이나 박스의 투명도를 설정한다.
            -------------------------------------
            font : 사용할 글꼴을 선택합니다. 이 글꼴은 Image.py가 있는 폴더의 fonts 폴더 내에 있으면 인식합니다.
            -------------------------------------
            font_size : 폰트의 크기를 지정한다.

            0 : 폰트의 크기를 이미지 크기에 맞게 비례하여 지정한다.
            1 이상 : 해당 크기에 맞게 표시한다.
            -------------------------------------
            option:
                - TextWithBackground: 텍스트에 배경을 줍니다.
                - PolygonToRectangle: 폴리곤을 박스로 변환합니다.
                - PolygonAndRectangle: 폴리곤 데이터가 있을 경우 박스와 폴리곤 모두 표시합니다.
                - PolygonToRectangleTextWithBackground: 텍스트에 배경과 폴리곤 데이터를 박스 데이터로 표시합니다.
                - PolygonAndRectangleTextWithBackground: 텍스트에 배경과 폴리곤 데이터와 박스 데이터 모두 표시합니다.
                
        """
        # Option is not Work
        if 'areaInImage' in annotation:
            areaInImage = annotation['areaInImage']
            coordinates = areaInImage['coordinates'] if 'coordinates' in areaInImage else None
            XY = None
            if 'type' in areaInImage:
                opacity = int(255 * opacity)
                sel_type = areaInImage['type']
                
                fill_color = (color[0],color[1],color[2],opacity)
                if sel_type in ['polygon','Polygon']:
                    if option in ["PolygonToRectangle", "PolygonToRectangleTextWithBackground"]:
                        sel_type="rectangle"
                        poly_info = utils.polygonToXY(coordinates)
                        coordinates = poly_info['diagonal']
                    else:
                        XY = utils.polygonToXY(coordinates)
                        coordinates = sum(coordinates, [])
                        draw_image.polygon(coordinates, fill=fill_color)
                        if option in ['PolygonAndRectangleTextWithBackground']:
                            sel_type="rectangle2"
                            coordinates = XY['diagonal']
                if sel_type in ['rectangle','Rectangle', 'mbr','bbox','BBOX','rectangle2']:
                    if sel_type in ['rectangle2']:
                        draw_image.rectangle(coordinates, outline=fill_color)
                    else:
                        draw_image.rectangle(coordinates, fill=fill_color)
                    XY = {'diagonal':coordinates}
                
                opacity = 255
        if 'annotationText' in annotation:
            fill_color = (color[0],color[1],color[2],opacity)
            xy1 = XY['diagonal'][0:2]
            xy2 = XY['diagonal'][2:4]
            font, font_size = self._get_font_(font,font_size)
            text = annotation['annotationText']
            x = xy1[0] if xy1[0]<xy2[0] else xy2[0]
            y = xy1[1] if xy1[1]<xy2[1] else xy2[1]
            y = y - (font_size*1.2)
            if y<0:
                y = xy1[1] if xy1[1]>xy2[1] else xy2[1]
                y + (font_size*1.2)
            if option in ['TextWithBackground', 'PolygonToRectangleTextWithBackground','PolygonAndRectangleTextWithBackground']:
                width = x+utils.str_to_byte(text)*+font_size*0.5
                coordinates = [x,y,width,y+(font_size*1.2)]
                draw_image.rectangle(coordinates, fill=fill_color)
                fill_color = (255,255,255,opacity)
            draw_image.text((x,y), text, fill=fill_color, font=font)

    def set_annotation(self, annotation):
        """
            # set_annotation : annotation을 설정합니다.

            annotation : list 혹은 dict 데이터를 받습니다. STPhoto Type의 양식을 따릅니다.
        """
        if isinstance(annotation, list) is True:
            self._annotation_ = annotation
        elif isinstance(annotation, dict) is True:
            self._annotation_ = list(annotation)
        else:
            raise SupportFormatError(type(annotation))
    
    def add_annotation(self, annotation):
        """
            # add_annotation : annotation을 추가합니다.

            annotation : list 혹은 dict 데이터를 받습니다. STPhoto Type의 양식을 따릅니다.
        """
        if self._annotation_ is None:
            self._annotation_=[]
        if isinstance(annotation, list) is True:
            self._annotation_.extend(annotation)
        elif isinstance(annotation, dict) is True:
            self._annotation_.append(annotation)
        else:
            raise SupportFormatError(type(annotation))

    def get_annotation(self):
        """
            # get_annotation : annotation을 반환합니다.
        """
        return self._annotation_

    def create_thumbnail(self, image_name = "", image_size = (128,128), image_path = ""):
        """
            # create_thumbnail : thumbnail 생성합니다.

            image_size : 조정할 이미지 크기입니다.
            -------------------------------------
            image_name : 생성할 thumbnail 이름입니다.
            
            image_name is "" : 동일한 이름 사용합니다.
            image_name is None : 랜덤한 이름 사용합니다.
            image_name is TEXT : 입력된 이름 사용합니다.
            -------------------------------------
            image_path : thumbnail를 저장할 경로입니다.

            image_path is "" : 기존 경로에 thumbnail 이름을 추가해서 저장합니다.
            image_path is None : 기존 경로에 생성합니다.
        """
        image = self._get_image_(is_new=True)
        if image_path == "":
            image_path = self._path_ + 'thumbnail'
        elif image_path is None:
            image_path = self._path_
        image_path = utils.create_folder(image_path)
        try:
            image.thumbnail(image_size)
        except:
            pass
        self.save(image_path, image_name=image_name, image=image)
        return image_path

    def save(self, create_folder, image_name = "", image_format = "", is_with_exif = True, image=None):
        """
            # save : 이미지를 파일로 저장합니다.

            create_folder : 이미지를 저장할 폴더 경로입니다.
            -------------------------------------
            is_with_exif : EXIF 메타 데이터까지 저장할 것인지 여부 값입니다.
            -------------------------------------
            image : 저장할 이미지 객체(Pillow Object)입니다.

            image is None : 기본 객체입니다.
            image is Pillow Object : Pillow Object 저장합니다.
            -------------------------------------
            image_name : 저장할 파일 이름입니다.

            image_name is "" : 동일한 이름 사용합니다.
            image_name is None : 랜덤한 이름 사용합니다.
            image_name is TEXT : 입력된 이름 사용합니다.
            -------------------------------------
            image_foramt : 저장할 파일의 포맷입니다.

            image_format is "" : 동일한 포맷 사용합니다.
            image_format is None : png 사용합니다.
            image_format is TEXT : 입력된 포맷 사용합니다.
                - 지원 Format : 'BMP','EPS','GIF','ICNS','ICO',
                                'IM','JPEG','MSP','PCX','PNG',
                                'PPM','SGI','SPIDER','WEBP',
                                'XBM','PALM','PDF','XV'
        """
        image = self._get_image_(image)        
        image = image.convert("RGB")
        
        #create_folder 기본 값 처리
        create_folder = utils.create_folder(create_folder)

        # image_format 기본 값 처리
        ext = self._file_name_.split(".")[-1]
        if image_format is None:
            image_format = "png"
        elif  image_format == "":
            image_format = ext
        else:
            support_format = ['BMP','EPS','GIF','ICNS','ICO','IM','JPEG','MSP','PCX','PNG','PPM','SGI','SPIDER','WEBP','XBM','PALM','PDF','XV']
            if not(image_format.upper() in support_format):
                raise SupportFormatError(image_format)

        image_format = image_format.lower().replace(".","")

        if image_format in ['PNG']:
            image = image.convert("RGBA")

        # image_name 기본 값 처리
        if image_name == "":
            image_name = self._file_name_.split("."+ext)[0] + "." + image_format
        elif image_name is None:
            image_name = utils.create_name(image_format, create_folder)
        else:
            image_name = image_name+"."+image_format
        
        full_path = create_folder+image_name

        # image EXIF(META) 정보 유지
        if is_with_exif is True:
            bexif = self._extract_bexif_(image)
            if bexif is not None:
                image.save(full_path, exif=bexif)
                return full_path

        image.save(full_path)
        return full_path

    def delete(self):
        """
            # delete : 다운로드 한 이미지를 삭제합니다.
        """
        os.remove(self._path_+self._file_name_)
    
    def get_info(self):
        """
            # get_info : 이미지의 정보를 가져옴니다. (Include EXIF)
        """
        result = {"Width":None, "Height":None, "Latitude":None, "Longitude":None, 
                "Altitude":None, "Time":None, "HorizontalAngle":None, 
                "Direction2d":None, "Distance":None}
        
        # 크기
        result['Width'], result['Height'] = self.get_size()

        # 위치 정보
        location = self.get_location()
        if location is not None:
            result['Longitude'], result['Latitude'] = location
        result['Altitude'] = self.get_altitude()
        
        # 시간
        result['Time'] = self.get_datetime()

        # 앵글 각도
        result['HorizontalAngle'] = 66

        # 방향
        result['Direction2d'] = self.get_direction()
        
        # 거리
        result['Distance'] = self.get_distance()

        return result
    
    def get_size(self):
        return self._get_image_().size

    def get_location(self, type=""):
        """
            # get_location : 이미지의 위치정보를 가져옵니다.

            type : 반환되는 형태를 말합니다.

            type is "" : (Longitude, Latitude) 형태로 반환됩니다.
            type is None : (Longitude, Latitude) 형태로 반환됩니다.
            type is "dictionary" :  {"Longitude": Longitude, "Latitude": Latitude} 형태로 반환됩니다.
            type is "point" : POINT(Longitude Latitude) 형태로 반환됩니다.
        """
        exif = self._exif_
        lon=None
        lat=None
        if "GPS GPSLongitude" in exif.keys():
            ref = None
            if "GPS GPSLongitudeRef" in exif.keys():
                ref = exif["GPS GPSLongitudeRef"]
            lon = utils.exif_to_data(exif["GPS GPSLongitude"], ref)
        if "GPS GPSLatitude" in exif.keys():
            ref = None
            if "GPS GPSLatitudeRef" in exif.keys():
                ref = exif["GPS GPSLatitudeRef"]
            lat = utils.exif_to_data(exif["GPS GPSLatitude"], ref)
        
        if lon is not None and lat is not None:
            if type == "dictionary":
                return {"Longitude": lon, "Latitude": lat}
            elif type=="point": 
                return "POINT(" + str(lon) + " " + str(lat) + ")"
            else:
                return (lon, lat)
        return None

    def get_altitude(self, type=""):
        """
            # get_altitude : 이미지의 altitude정보를 가져옵니다.

            type : 반환되는 형태를 말합니다.

            type is "" : altitude 형태로 반환됩니다.
            type is None : altitude 형태로 반환됩니다.
            type is "dictionary" :  {"altitude": altitude} 형태로 반환됩니다.
        """
        exif = self._exif_
        if "GPS GPSAltitude" in exif.keys():
            ref = None
            if "GPS GPSAltitudeRef" in exif.keys():
                ref = exif["GPS GPSAltitudeRef"]
            altitude = utils.exif_to_data(exif["GPS GPSAltitude"], ref)
            if type=="dictionary":
                return {"Altitude": altitude}
            else:
                return altitude
        return None

    def get_datetime(self, type=""):
        """
            # get_datetime : 이미지에 있는 시간 데이터를 가져옵니다.
            
            type : 반환되는 형태를 말합니다.

            type is "timestamp_with_dictionary" : timestamp으로 Dictionary 형태로 반환됩니다.
            type is "timestamp" : timestamp으로 반환됩니다.
            type is "date_with_dictionary" : date으로 Dictionary 형태로 반환됩니다.
            type is "date" : date으로 반환됩니다.
            type is None or type is "" : date으로 반환됩니다.
        """
        exif = self._exif_
        if "Image DateTime" in exif.keys():
            datetime_ = str(exif["Image DateTime"]).split(" ")
            date_ = datetime_[0].replace(":", '-') + " " + datetime_[1]
            date_ = utils.check_format_date(date_)
        else:
            date_ = "2000-01-01 00:00:00"
        timestamp_ = utils.datatime_to_timestamp(date_)
        
        if type=="timestamp_with_dictionary":
            return {"Timestamp" : timestamp_}
        elif type == "timestamp":
            return timestamp_
        elif type == "date_with_dictionary":
            return {"Date": date_}
        else:
            return date_

    def get_direction(self, type=""):
        """
            # get_direction : 이미지에 있는 방향 데이터를 가져옵니다.
            
            type : 반환되는 형태를 말합니다.

            type is "dictionary" : {"Direction": Direction} 형태로 반환됩니다.
            type is "" or type is None : Direction 형태로 반환됩니다.
        """
        exif = self._exif_
        if "GPS GPSImgDirection" in exif.keys():
            ref = None
            if "GPS GPSImgDirectionRef" in exif.keys():
                ref = exif["GPS GPSImgDirectionRef"]
            data = utils.exif_to_data(exif["GPS GPSImgDirection"], ref)
            if type=="dictionary":
                return {"Direction": data}
            else:
                return data
        return None

    def get_distance(self, type=""):
        """
            # get_distance : 이미지에 있는 방향 데이터를 가져옵니다.
            
            type : 반환되는 형태를 말합니다.

            type is "dictionary" : {"Distance": Distance} 형태로 반환됩니다.
            type is "" or type is None : Distance 형태로 반환됩니다.
        """
        exif = self._exif_
        if "GPS GPSDestDistance" in exif.keys():
            distance = utils.exif_to_data(exif["GPS GPSDestDistance"], exif["GPS GPSDestDistance"])
            if type=="dictionary":
                return {"Distance": distance}
            else:
                return distance
        else:
            return None
    
    def to_numpy(self):
        """
            # to_numpy : 이미지 데이터를 Numpy 데이터로 변환합니다.
        """
        image = self._get_image_()
        return np.array(image)

    def draw_annotations(self, annotations,opacity=0.5, option="", font='TmonMonsori',font_size=0):
        """
            # draw_annotations : 이미지에 annotation 데이터에 따라 그려줍니다.

            annotations : STPhoto의 annotations Dictionary 데이터만 사용 가능합니다.

            annotations is "" or annotations is not dict : 아무것도 하지 않습니다.
            annotations type is dict : dDictionary 데이터에 따라 이미지를 변형 및 위에 그립니다.
            -------------------------------------
            opacity : 객체를 식별할 폴리곤이나 박스의 투명도를 설정한다.
            -------------------------------------
            font : 사용할 글꼴을 선택합니다. 이 글꼴은 Image.py가 있는 폴더의 fonts 폴더 내에 있으면 인식합니다.
            -------------------------------------
            font_size : 폰트의 크기를 지정한다.

            0 : 폰트의 크기를 이미지 크기에 맞게 비례하여 지정한다.
            1 이상 : 해당 크기에 맞게 표시한다.
            -------------------------------------
            option:
                - TextWithBackground: 텍스트에 배경을 줍니다.
                - PolygonToRectangle: 폴리곤을 박스로 변환합니다.
                - PolygonToRectangleTextWithBackground: 위 옵션 모드 적용
                
        """
        image = self._get_image_()
        image = image.convert("RGBA")
        
        if annotations is None or not isinstance(annotations, dict) == 0:
            return
        y, x, z = self.to_numpy().shape
        colors = utils.create_colors(len(annotations))
        # 도화지 가져오기
        mask_image = pImage.fromarray(np.uint8(np.zeros((y, x, z + 1))))
        draw_mask_image = ImageDraw.Draw(mask_image)
        for idx in range(len(annotations)):
            annotation = annotations[idx]
            self._draw_annotation_(draw_mask_image, annotation, colors[idx], opacity=opacity, 
                                                    option=option, font=font, font_size=font_size)
        if mask_image:
            image = pImage.alpha_composite(image, mask_image)
        self._image_ = image

    def to_gray_numpy(self):
        """
            # to_gray_numpy : 이미지를 그레이스케일로 변경 후 넘파이 데이터로 반환합니다.
        """
        image = self._get_image_()
        image = image.convert("LA")
        return np.array(image)

    def get_path(self):
        return self._path_
    
    def get_file_name(self):
        return self._file_name_
    
    def to_stphoto(self):
        info = self.get_info()
        return {
            "type":"stphoto",
            "uri":self._uri_,
            "width":info['Width'],
            "height":info['Height'],
            "latitude":info['Latitude'],
            "longitude":info['Longitude'],
            "altitude":info['Altitude'],
            "time":info['Time'],
            "annotations":self.get_annotation(),
            "fov":{
                "horizontalAngle":info['HorizontalAngle'],
                "verticalAngle":None,
                "direction2d":info['Direction2d'],
                "distance":info['Distance'],
                "directionVectior":None
            }
        }
    def to_stphoto_as_json(self):
        return json.dumps(self.to_stphoto(), indent='\t', sort_keys=True, default=utils.default_DICT_TO_JSON)
    
    def to_stphoto_as_json_file(self, path, file_name):
        path = utils.create_folder(path)
        file_name = file_name.replace("."+file_name.split(".")[-1],"")
        path = path + file_name + ".json"
        data = self.to_stphoto()
        
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent='\t', sort_keys=True, default=utils.default_DICT_TO_JSON)
        return path

    def display(self):
        print(self.to_stphoto_as_json())