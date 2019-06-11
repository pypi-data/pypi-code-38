"""
pypsxlib: Unofficial python library for reading and writing Agisoft Photoscan/Metashape psx project files.

Copyright (c) 2019 Luke Miller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime

from json import dumps
import json
import os
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union
import warnings
from xml.etree.ElementTree import fromstring
import xml.etree.ElementTree as ET
from xml import etree
from zipfile import ZipFile


from dataclasses_json import dataclass_json
from lxml import etree
from PIL import Image as PILimage  # pillow package
from xmljson import gdata

__version__ = "0.1.2"
__version_psx__ = "1.2.0"


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError("Type %s not serializable" % type(obj))


@dataclass_json
@dataclass
class Thumbnails:
    camera_ids: List[str] = field(default_factory=list)
    thumb_paths: List[str] = field(default_factory=list)
    version: str = None

    def load_psx(self, fname):
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError
        document = None
        with ZipFile(fpath, 'r') as zf:
            # inside the zip is probably just one "doc.xml" file.
            for docfname in zf.filelist:
                if docfname.orig_filename == "doc.xml":
                    xmlstr = zf.read(docfname)
                    # convert the xml string into xml tree, take the document node and convert to json string, load to dataclass
                    bf = dumps(gdata.data(fromstring(xmlstr)))
                    jdata = json.loads(bf)["thumbnails"]
                    self.version = jdata.get("version", None)
                    for cdata in jdata.get("thumbnail", []):
                        self.thumb_paths.append(cdata["path"])
                        self.camera_ids.append(cdata["camera_id"])
                else:
                    warnings.warn("Thumbnail loading ignores thumbnails images in zip and uses data from doc.xml.")
        return self


    def xml(self):
        root = etree.Element("thumbnails", version=__version_psx__)
        for i, c in enumerate(self.camera_ids):
            root.append(etree.Element("thumbnail", camera_id=c, path=self.thumb_paths[i]))
        """
<?xml version="1.0" encoding="UTF-8"?>
<thumbnails version="1.2.0"/>
---
<?xml version="1.0" encoding="UTF-8"?>
<thumbnails version="1.2.0">
  <thumbnail camera_id="0" path="c0.jpg"/>
  <thumbnail camera_id="1" path="c1.jpg"/>
</thumbnails>

        """
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())


def generate_zip(obj, path, zipfname, extra_files=None):
    extra_files = extra_files if extra_files else []
    doc_file = path.joinpath("doc.xml")
    print(f"  save {doc_file}")
    obj.save(doc_file)
    zip_file = path.joinpath(zipfname)
    with ZipFile(zip_file, 'w') as fzip:
        for extra_file in extra_files:
            fzip.write(extra_file, arcname=Path(extra_file).name)
        fzip.write(doc_file, arcname="doc.xml")
    doc_file.unlink()
    for extra_file in extra_files:
        Path(extra_file).unlink()


@dataclass_json
@dataclass
class Property:
    name: str = ""
    value: str = ""
    text: str = ""

    def xml(self):
        root = etree.Element("property", name=self.name, value=str(self.value))
        return root


@dataclass_json
@dataclass
class Photo:
    path: str = None
    meta: List[Property] = field(default_factory=list)

    def generate_meta(self):
        # generate meta properties
        file_size = os.stat(self.path).st_size
        mod_date = os.stat(self.path).st_mtime
        mod_date = datetime.utcfromtimestamp(mod_date).strftime('%Y-%m-%d %H:%M:%S')
        im = PILimage.open(self.path)
        width, height = im.size
        self.meta.append(Property(name="File/ImageHeight", value=str(height)))
        self.meta.append(Property(name="File/ImageWidth", value=str(width)))
        self.meta.append(Property(name="System/FileModifyDate", value=mod_date))
        self.meta.append(Property(name="System/FileSize", value=str(file_size)))

    def xml(self):
        root = etree.Element("photo", path=self.path)
        meta = etree.Element("meta")
        root.append(meta)
        for prop in self.meta:
            meta.append(prop.xml())
        """
      <photo path="../../../../../comparephotos/test/file0003_1.png">
        <meta>
          <property name="File/ImageHeight" value="1080"/>
          <property name="File/ImageWidth" value="1920"/>
          <property name="System/FileModifyDate" value="2019:04:08 19:29:32"/>
          <property name="System/FileSize" value="2336461"/>
        </meta>
      </photo>
        """
        return root


@dataclass_json
@dataclass
class FrameCamera:  # reduced version used in Chunk, full version used in Frame
    camera_id: int = None
    photo: Photo = None #List[Photo] = field(default_factory=list)

    def xml(self, camera_id=None):
        self.camera_id = camera_id if camera_id else self.camera_id
        root = etree.Element("camera", camera_id=camera_id)
        root.append(self.photo.xml())
        """        
    <camera camera_id="0">
      <photo path="../../../../../comparephotos/test/file0003_0.png">
        <meta>
          <property name="File/ImageHeight" value="1080"/>
          <property name="File/ImageWidth" value="1920"/>
          <property name="System/FileModifyDate" value="2019:04:08 19:29:29"/>
          <property name="System/FileSize" value="2257248"/>
        </meta>
      </photo>
    </camera>
        """
        return root


@dataclass_json
@dataclass
class ChunkCamera:  # reduced version used in Chunk
    id: int = None
    sensor_id: int = None
    label: str = None
    transform: str = None
    rotation_covariance: str = None
    location_covariance: str = None

    def xml(self, camera_id=None):
        """
        <camera id="1" sensor_id="0" label="frame000000">
            <transform>-9.9208283570125888e-01 -1.0191056933652956e-01 7.3388575162985942e-02 -7.6303195906841914e-01 1.0558756234029021e-01 -9.9324647973765101e-01 4.8090510163641922e-02 4.5558309634776001e-01 6.7992012663136897e-02 5.5458690448552950e-02 9.9614327276137726e-01 -7.9148114957875757e+00 0 0 0 1</transform>
            <rotation_covariance>9.4091605131524275e-08 -2.2483795612176852e-08 -6.2581112138597624e-08 -2.2483795612176852e-08 9.9898068284822843e-08 -1.2882007167597330e-08 -6.2581112138597611e-08 -1.2882007167597330e-08 1.7844663980461062e-07</rotation_covariance>
            <location_covariance>1.7050726462596322e-06 5.7735210448670669e-07 9.6998038482642297e-08 5.7735210448670669e-07 7.0770155106778702e-07 -2.8846541918156092e-07 9.6998038482642297e-08 -2.8846541918156092e-07 1.4315366423064984e-06</location_covariance>
        </camera>
        """
        self.id = camera_id if camera_id else self.id
        root = etree.Element("camera", id=str(self.id), sensor_id=str(self.sensor_id), label=self.label)
        for element in ["transform", "rotation_covariance", "location_covariance"]:
            attr = getattr(self, element, None)
            if attr:
                xml_attr = etree.Element(element)
                xml_attr.text = attr
                root.append(xml_attr)
        return root


@dataclass_json
@dataclass
class Frame:
    version: str = ""
    cameras: List[FrameCamera] = field(default_factory=list)
    thumbnails: Thumbnails = None  #List[Thumbnail] = field(default_factory=list)
    point_cloud: str = ""  # TODO: replace with PointCloud class
    model: str = ""  # TODO: replace with Model class

    def load_psx(self, fname):
        """
<?xml version="1.0" encoding="UTF-8"?>
<frame version="1.2.0">
  <cameras>
    <camera camera_id="0">
      <photo path="../../../../../voltfvideoalign/saves/VID_20190610_130300136/images/frame000000.png">
        <meta>
          <property name="File/ImageHeight" value="1080"/>
          <property name="File/ImageWidth" value="1920"/>
          <property name="System/FileModifyDate" value="2019:06:10 14:52:57"/>
          <property name="System/FileSize" value="1651700"/>
        </meta>
      </photo>
    </camera>
  </cameras>
  <thumbnails path="thumbnails/thumbnails.zip"/>
  <point_cloud path="point_cloud.3/point_cloud.zip"/>
  <model id="1" path="model.1/model.zip"/>
</frame>
        """
        warnings.warn("Frame loading of `point_cloud` and `model` not implemented yet.")
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError
        document = None
        with ZipFile(fpath, 'r') as zf:
            # inside the zip is probably just one "doc.xml" file.
            for docfname in zf.filelist:
                xmlstr = zf.read(docfname)
                # convert the xml string into xml tree, take the document node and convert to json string, load to dataclass
                bf = dumps(gdata.data(fromstring(xmlstr))["frame"])
                jdata = json.loads(bf)
                self.version = jdata.get("version", "")
                for cdata in jdata.get("cameras", [])["camera"]:
                    pdata = cdata["photo"]
                    photo = Photo(path=pdata["path"])
                    for prop in pdata["meta"]["property"]:
                        photo.meta.append(Property(**prop))

                    self.cameras.append(FrameCamera(camera_id=cdata["camera_id"], photo=photo))

                if "point_cloud" in jdata:
                    #self.point_cloud = jdata["point_cloud"]
                    warnings.warn(f"Loading point_cloud data not implemented yet {jdata['point_cloud']}. "
                                  "Please open an issue at https://gitlab.com/dodgyville/pypsxlib/issues")

                if "model" in jdata:
                    # self.model = jdata["model"]
                    warnings.warn(f"Loading model data not implemented yet {jdata['model']}. "
                                  "Please open an issue at https://gitlab.com/dodgyville/pypsxlib/issues")

                if "thumbnails" in jdata:  # load from file
                    thumbnail_file = jdata["thumbnails"].get("path", None)
                    if not thumbnail_file:
                        warnings.warn(f"Unable to load thumbnails for this frame {jdata['thumbnails']}")
                    self.thumbnails = Thumbnails().load_psx(fpath.parent.joinpath(thumbnail_file))

        return self

    def xml(self):
        root = etree.Element("frame", version=__version_psx__)
        cameras = etree.Element("cameras")
        for i, camera in enumerate(self.cameras):
            warnings.warn("need to add camera_id to xml here.")
            cameras.append(camera.xml(camera_id=str(i)))
        """
<?xml version="1.0" encoding="UTF-8"?>
<frame version="1.2.0">
  <thumbnails path="thumbnails/thumbnails.zip"/>
</frame>
        """
        root.append(cameras)
        warnings.warn("Converting Frame thumbnails to zip uses hardcoded filepath instead of existing.")
        root.append(etree.Element("thumbnails", path="thumbnails/thumbnails.zip"))
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())

    def generate_psx(self, index, chunk_path):
        # chunk_path is the Pathlib object to the chunk directory
        frame_path = chunk_path.joinpath(f"{index}")
        print(f"  create frame {frame_path}")
        if not frame_path.is_dir():
            # create the chunk directory and the files in it.
            # a chunk.zip with a doc.xml inside it
            # and a frame? directory
            frame_path.mkdir()
        thumbnails_path = frame_path.joinpath("thumbnails")
        if not thumbnails_path.is_dir():
            thumbnails_path.mkdir()
        extra_files = []
        self.thumbnails = Thumbnails()
        warnings.warn("Thumbnails are currently generated afresh when project saved. This will be changing in a future version to make it explicit. "
                      "Please open an issue at https://gitlab.com/dodgyville/pypsxlib/issues")
        for c, camera in enumerate(self.cameras):
            camera_path = Path(camera.photo.path)
            if not camera_path.is_file():
                camera_path = frame_path.joinpath(camera_path)
            if not camera_path.is_file():
                print(f"Unable to find camera path {camera.photo.path} or {camera_path}")
            im = PILimage.open(camera_path)
            im.thumbnail((192, 108), PILimage.ANTIALIAS)
            p = thumbnails_path.joinpath(f"c{c}.jpg")
            im.save(p, "JPEG", optimize=True)
            extra_files.append(p.as_posix())
            self.thumbnails.camera_ids.append(str(c))
            self.thumbnails.thumb_paths.append(p.name)
        generate_zip(self.thumbnails, thumbnails_path, "thumbnails.zip", extra_files)

        generate_zip(self, frame_path, "frame.zip")


@dataclass_json
@dataclass
class Resolution:
    width: int = None
    height: int = None

    def xml(self):
        root = etree.Element("resolution", width=str(self.width), height=str(self.height))
        return root


@dataclass_json
@dataclass
class Band:
    label: str = None

    def xml(self):
        #  <band label="Red"/>
        return etree.Element("band", label=self.label)


@dataclass_json
@dataclass
class Sensor:
    label: str = None
    type: str = None
    resolution: Resolution = None
    properties: List[Property] = field(default_factory=list)
    bands: List[Band] = field(default_factory=list)
    data_type: str = None

    covariance: Any = None
    calibration: Any = None


    def xml(self, sensor_id):
        warnings.warn("Not all sensor fields (eg covariance, calibration) are exported.")
        d = {"id": sensor_id}
        if self.type:
            d["type"] = self.type
        if self.label:
            d["label"] = self.label
        root = etree.Element("sensor", **d)
        root.append(self.resolution.xml())
        for property in self.properties:
            root.append(property.xml())

        bands = etree.Element("bands")
        for band in self.bands:
            bands.append(band.xml())
        root.append(bands)
        data_type = etree.Element("data_type")
        if self.data_type:
            data_type.text = self.data_type
            root.append(data_type)
        """
    <sensor id="0" label="unknown" type="frame">
      <resolution width="640" height="480"/>
      <property name="layer_index" value="0"/>
      <bands>
        <band label="Red"/>
        <band label="Green"/>
        <band label="Blue"/>
      </bands>
      <data_type>uint8</data_type>
    </sensor>
        """
        return root

@dataclass_json
@dataclass
class TransformComponent:  # this is a custom class not obvious from the psx project format
    locked: bool = False
    value: str = ""
    def xml(self):
        #  <band label="Red"/>
        pass


@dataclass_json
@dataclass
class Transform:
    rotation: TransformComponent = None
    translation: TransformComponent = None
    scale: TransformComponent = None

    def xml(self):
        root = etree.Element("transform")
#        if self.rotation:
#            d["rotation"] = self.rotation
#        if self.label:
#            d["translation"] = self.translation
#        if self.scale:
#            d["scale"] = self.scale
        for e in ["rotation", "translation", "scale"]:
            d = self.__dict__[e]
            element = etree.Element(e, locked=str(d.locked).lower())
            element.text = str(d.value)
            root.append(element)
        return root



@dataclass_json
@dataclass
class Model:
    id: int = None
    def xml(self):
        #  <band label="Red"/>
        return etree.Element("model", id=self.id)



@dataclass_json
@dataclass
class Region:
    center: str = ""
    size: str = ""
    R: str = ""
    def xml(self):
        """
        <region>
            <center>-5.7719340774472917e-02 -4.5149666204502842e-01 -5.3048672015010094e+00</center>
            <size>9.8749252885371099e+00 1.0014738640192867e+01 1.3761102775304394e+01</size>
            <R>-1.7463425111662328e-01 -2.3108323557529828e-01 9.5713291478926144e-01 9.8444515510169017e-01 -2.1971279982058858e-02 1.7431293541432710e-01 -1.9251361867291757e-02 9.7268586968866855e-01 2.3132570971306543e-01</R>
        </region>
        """
        root = etree.Element("region")
        for element in ["center", "size", "R"]:
            attr = getattr(self, element, None)
            if attr:
                xml_attr = etree.Element(element)
                xml_attr.text = attr
                root.append(xml_attr)
        return root


@dataclass_json
@dataclass
class Settings:
    properties: List[Property] = field(default_factory=list)


@dataclass_json
@dataclass
class Chunk:
    name: str = None
    label: str = None
    enabled: bool = None
    version: str = ""
    sensors: List[Sensor] = field(default_factory=list)
    cameras: List[ChunkCamera] = field(default_factory=list)
    models: List[Model] = field(default_factory=list)
    frames: List[Frame] = field(default_factory=list)
    transform: Transform = None
    reference: Any = None
    region: Region = None
    meta: List[Property] = field(default_factory=list)
    settings: List[Property] = field(default_factory=list)

    def defaults(self):
        self.settings.append(Property(name="accuracy_tiepoints", value="1"))
        self.settings.append(Property(name="accuracy_cameras", value="10"))
        self.settings.append(Property(name="accuracy_cameras_ypr", value="10"))
        self.settings.append(Property(name="accuracy_markers", value="0.005"))
        self.settings.append(Property(name="accuracy_scalebars", value="0.001"))
        self.settings.append(Property(name="accuracy_projections", value="0.1"))

    def load_psx(self, fname):
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError
        chunk = None
        with ZipFile(fpath, 'r') as zf:
            for chunkfname in zf.filelist:
                xmlstr = zf.read(chunkfname)
                bf = dumps(gdata.data(fromstring(xmlstr))["chunk"])
                chunk_data = json.loads(bf)
                chunk = Chunk(enabled=chunk_data["enabled"], label=chunk_data["label"], version=chunk_data["version"])
                unhandled_fields = list(chunk_data.keys())
                for i in ["transform", "sensors", "settings", "cameras", "meta", "enabled", "label", "version", "reference", "frames", "region", "models"]:
                    if i not in unhandled_fields:
                        pass
                    else:
                        unhandled_fields.remove(i)

                if unhandled_fields:
                    warnings.warn(f"Unhandled attributes in chunk data {unhandled_fields}. ",
                                  "Please open an issue at https://gitlab.com/dodgyville/pypsxlib/issues")
#                chunk = Chunk(**chunk_data)
                #document = Document(version=j["version"], next_id=j["chunks"]["next_id"], active_id=j["chunks"]["active_id"])
                for key, data in chunk_data["sensors"].items():
                    if key == "sensor":
                        warnings.warn("Not all sensor fields (eg covariance, calibration) are loaded.")
                        sensor = Sensor(
                                resolution=Resolution(**data["resolution"]),
                                type=data["type"],
                                label=data["label"])
                        if "property" in data:
                            sensor.properties.append(Property(**data["property"]))
                        chunk.sensors.append(sensor)

                for key, data in chunk_data["cameras"].items():
                    if key == "camera":
                        cameras_data = [cameras_data] if type(data) in [dict] else data
                        for camera_data in cameras_data:
                            if "transform" in camera_data:
                                warnings.warn("Camera in chunk loads transform data as a string not an object. "
                                              "Please open an issue at https://gitlab.com/dodgyville/pypsxlib/issues")
                            chunk.cameras.append(ChunkCamera(
                                id=camera_data.get("id", None),
                                sensor_id=camera_data.get("sensor_id", None),
                                label=camera_data.get("label", None),
                                transform=camera_data.get("transform", {}).get("$t", None),
                                rotation_covariance=camera_data.get("rotation_covariance", {}).get("$t", None),
                                location_covariance=camera_data.get("location_covariance", {}).get("$t", None),
                            ))
#                        chunk.cameras[-1].photo.path = Path(chunk.cameras[-1].photo.path).relative_to(fpath).as_posix()

                for prop in ["settings", "meta"]:
                    if prop in chunk_data:
                        settings = Settings()
                        setattr(chunk, prop, settings)
                    for key, data in chunk_data[prop].items():
                        if key == "property":
                            for prop in data:
                                settings.properties.append(Property(**prop))

                if "reference" in chunk_data:
                    chunk.reference = chunk_data["reference"].get("$t", None)

                if "transform" in chunk_data:
                    transform_data = chunk_data["transform"]
                    warnings.warn("Transform data in chunk loads as strings not objects "
                                  "Please open an issue at https://gitlab.com/dodgyville/pypsxlib/issues")

                    t = Transform()
                    for attr in ["rotation", "translation", "scale"]:
                        component = TransformComponent()
                        component.value = transform_data.get(attr, {}).get("$t", None)
                        component.locked = transform_data.get("locked", False)
                        if component.value:
                            setattr(t, attr, component)
                    chunk.transform = t

                for key, data in chunk_data["reference"].items():
                    if key == "property":
                        for prop in data:
                            chunk.settings.properties.append(Property(**prop))

                if "region" in chunk_data:
                    warnings.warn("Region in chunk loads data as strings not objects "
                                  "Please open an issue at https://gitlab.com/dodgyville/pypsxlib/issues")
                    region_data = chunk_data["region"]
                    chunk.region = Region(
                        center=region_data.get("center", {}).get("$t", None),
                        size=region_data.get("size", {}).get("$t", None),
                        R=region_data.get("R", {}).get("$t", None),
                    )

                for key in chunk_data["models"].keys():
                    if key == "model":
                        model_json = chunk_data["models"][key]
                        #cname = Path(fpath.parent, model_json["path"])
                        chunk.models.append(Model(id=model_json["id"]))
                        #chunk.frames.append(Frame().load_psx(cname))

                for key in chunk_data["frames"].keys():
                    if key == "frame":
                        frame_json = chunk_data["frames"][key]
                        cname = Path(fpath.parent, frame_json["path"])
                        chunk.frames.append(Frame().load_psx(cname))
        return chunk

    def xml(self):
        enabled = "true" if self.enabled else "false"
        if self.label:
            root = etree.Element("chunk", version=__version_psx__, enabled=enabled, label=self.label)
        else:
            root = etree.Element("chunk", version=__version_psx__, enabled=enabled)

        child_node = etree.Element("sensors", next_id=f"{len(self.sensors)}")
        for i, child in enumerate(self.sensors):
            child_xml = child.xml(sensor_id=str(i))  #etree.Element("sensor", id=f"{i}")
            child_node.append(child_xml)
        root.append(child_node)

        child_node = etree.Element("cameras", next_id=f"{len(self.cameras)}", next_group_id="0")
        warnings.warn("Not sure what chunk.cameras.next_group_id is for, defaulting to zero.")
        for i, child in enumerate(self.cameras):
            child_node.append(child.xml(i))
        root.append(child_node)

        child_node = etree.Element("frames", next_id=f"{len(self.frames)}")
        for i, child in enumerate(self.frames):
            child_xml = etree.Element("frame", id=f"{i}", path=f"{i}/frame.zip")
            child_node.append(child_xml)
        root.append(child_node)

        if self.transform:
            root.append(self.transform.xml())

        reference = etree.Element("reference")
        reference.text = 'LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
        root.append(reference)

        if self.region:
            root.append(self.region.xml())

        settings = etree.Element("settings")
        for property in self.settings.properties:
            settings.append(property.xml())
        root.append(settings)

        meta = etree.Element("meta")
        for property in self.meta.properties:
            meta.append(property.xml())
        root.append(meta)

        """
<?xml version="1.0" encoding="UTF-8"?>
<chunk version="1.2.0" label="Chunk 1" enabled="true">
  <sensors next_id="0"/>
  <cameras next_id="0" next_group_id="0"/>
  <frames next_id="1">
    <frame id="0" path="0/frame.zip"/>
  </frames>
  <reference>LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]</reference>
  <settings>
    <property name="accuracy_tiepoints" value="1"/>
    <property name="accuracy_cameras" value="10"/>
    <property name="accuracy_cameras_ypr" value="10"/>
    <property name="accuracy_markers" value="0.005"/>
    <property name="accuracy_scalebars" value="0.001"/>
    <property name="accuracy_projections" value="0.1"/>
  </settings>
</chunk>
        """
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())

    def generate_psx(self, index, doc_path):
        chunk_path = doc_path.joinpath(f"{index}")
        print(f" create {chunk_path}")
        if not chunk_path.is_dir():
            # create the chunk directory and the files in it.
            # a chunk.zip with a doc.xml inside it
            # and a frame? directory
            chunk_path.mkdir()

        for j, frame in enumerate(self.frames):
            frame.generate_psx(j, chunk_path)

        generate_zip(self, chunk_path, "chunk.zip")


@dataclass_json
@dataclass
class Document:
    name: str = ""
    version: str = ""
    path: str = ""

    next_id: int = None
    active_id: int = None

    chunks: List[Chunk] = field(default_factory=list)
    meta: List[Property] = field(default_factory=list)

    def defaults(self):
        self.meta.append(Property( name="Info/OriginalSoftwareName", value="pypsxlib"))
        self.meta.append(Property( name="Info/OriginalSoftwareVendor", value="Luke Miller"))
        self.meta.append(Property( name="Info/OriginalSoftwareVersion", value=__version__))

    def load_psx(self, fname):
        """
        Process a project.zip file from the top level.
        """
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError
        document = None
        with ZipFile(fpath, 'r') as zf:
            # inside the zip is probably just one "doc.xml" file.
            for docfname in zf.filelist:
                xmlstr = zf.read(docfname)
                # convert the xml string into xml tree, take the document node and convert to json string, load to dataclass
                bf = dumps(gdata.data(fromstring(xmlstr))["document"])
                j = json.loads(bf)
                document = Document(version=j["version"], next_id=j["chunks"]["next_id"], active_id=j["chunks"]["active_id"])
                # in the new example, j["chunks"]["chunk"] is a list of 5 dicts (id, path)
                for key in j["chunks"].keys():
                    if key == "chunk":
                        chunks_json = j["chunks"][key]
                        chunks_json = [chunks_json] if type(chunks_json) in [dict] else chunks_json
                        for chunk_json in chunks_json:
                            cname = Path(fpath.parent, chunk_json["path"])
                            document.chunks.append(Chunk().load_psx(cname))
        return document

    def xml(self):
        root = etree.Element("document", version=__version_psx__)
        chunks = etree.Element("chunks", next_id=f"{len(self.chunks)}", active_id="0")
        for i, chunk in enumerate(self.chunks):
            chunk_xml = etree.Element("chunk", id=f"{i}", path=f"{i}/chunk.zip")
            chunks.append(chunk_xml)
        root.append(chunks)
        meta = etree.Element("meta")

        for property in self.meta:
            meta.append(etree.Element("property", name=property.name, value=property.value))

        """
        meta.append(etree.Element("property", name="Info/OriginalSoftwareName", value="pypsxlib"))
        meta.append(etree.Element("property", name="Info/OriginalSoftwareVendor", value="Luke Miller"))
        meta.append(etree.Element("property", name="Info/OriginalSoftwareVersion", value=__version__))
        """
        root.append(meta)
        """
<?xml version="1.0" encoding="UTF-8"?>
<document version="1.2.0">
  <chunks next_id="1" active_id="0">
    <chunk id="0" path="0/chunk.zip"/>
  </chunks>
  <meta>
    <property name="Info/OriginalSoftwareName" value="Agisoft Metashape"/>
    <property name="Info/OriginalSoftwareVendor" value="Agisoft"/>
    <property name="Info/OriginalSoftwareVersion" value="1.5.2.7838"/>
  </meta>
</document>
        
        """
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())


@dataclass_json
@dataclass
class App:
    documents: List[Document] = field(default_factory=list)


@dataclass_json
@dataclass
class Project:
    name: str = None
    path: str = None
    apps: List[App] = field(default_factory=list)

    def defaults(self, chunk=True):
        """
        Create an empty project with one chunk
        """
        self.apps.append(App())
        document = Document()
        self.apps[0].documents.append(document)
        document.defaults()
        if chunk:
            self.add_chunk()

    def add_chunk(self):
        if not self.apps or not self.apps[0].documents:
            self.defaults()
        else:
            chunk = Chunk()
            chunk.defaults()
            self.apps[0].documents[0].chunks.append(chunk)
            self.apps[0].documents[0].chunks[-1].frames.append(Frame())
            self.apps[0].documents[0].chunks[-1].frames[0].thumbnails = Thumbnails()
        return self.apps[0].documents[0].chunks[-1]

    def load_psx(self, fname):
        """
        Load the top level psx file.
        """
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError

        with open(fname, "r") as f:
            xmlstr = f.read()
        # convert the xml string into xml tree, take the document node and convert to json string, load to dataclass
        bf = dumps(gdata.data(fromstring(xmlstr))["document"])
        document = Document.from_json(bf, infer_missing=True)
        if not self.apps:
            self.apps.append(App())
        dname = document.path.replace("{projectname}", self.name)
        dname = Path(fpath.parent, dname)
        # inside the psx file is a zipped project.zip file, process that now.
        document = Document().load_psx(dname)
        self.apps[-1].documents.append(document)
        return self

    def xml(self):
        root = etree.Element("document", version=__version_psx__, path="{projectname}.files/project.zip")
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, path=None, override=False):
        self.path = path if path else self.path
        project_path = Path(self.path)
        path = Path(self.path, self.name)
        files_path = path.with_suffix(".files")
        for p in [project_path, path, files_path]:
            if not p.is_dir():
                p.mkdir()
            elif not override:
                raise IsADirectoryError(f"directory {p} already exists")

        # go into files_path and create a directory per chunk and a high level project.zip contain doc.xml
        project_file = files_path.joinpath("project.zip")
        with ZipFile(project_file, 'w') as myzip:
            for app in self.apps:
                for doc in app.documents:
                    doc_file = files_path.joinpath("doc.xml")
                    doc.save(doc_file)
                    for i, chunk in enumerate(doc.chunks):
                        chunk.generate_psx(i, files_path)

                    myzip.write(doc_file, arcname="doc.xml")
                    doc_file.unlink()

        # create top level psx file
        psx_file = path.with_suffix(".psx")
        print(psx_file)
        with open(psx_file, "wb") as f:
            f.write(self.xml())


"""
<?xml version="1.0" encoding="UTF-8"?>
<document version="1.2.0" path="{projectname}.files/project.zip"/>
"""


def parse_xml(cwd, root, project_name):
    warnings.warn("`parse_xml` is a provisional function and may not exist in future versions.")
    # print out a psx project (call from parse_xmlfile)
    depth = " "*len(Path(cwd).parts)
    if root.text:
        print(depth, root.tag, root.attrib, root.text)
    else:
        print(depth, root.tag, root.attrib)

    if "path" in root.attrib:
        fname = root.attrib["path"]
        fname = fname.replace("{projectname}", project_name)
        fpath = Path(cwd, fname)
        if fpath.suffix == ".zip":
            print(depth,"z--", fpath.name)
            with ZipFile(fpath, 'r') as zf:
                for chunkfname in zf.filelist:
                    chunkfpath = Path(chunkfname.filename)
                    if chunkfpath.suffix == ".xml":
                        xmlstr = zf.read(chunkfname)
                        print(depth,"--z", chunkfpath.name)
                        cwd = Path(cwd).joinpath(fpath.parent)
                        xml = ET.fromstring(xmlstr)
                        #xmlprettyprint(xml)
                        parse_xml(cwd, xml, project_name)
                    else:
                        print(depth, "FILE IN ZIP",chunkfpath)
                        print()
        else:
            print(depth, "FILE", fpath)
            print()

    for child in root:
        parse_xml(cwd, child, project_name)


def parse_xmlfile(cwd, fname=None, project_name=None):
    warnings.warn("`parse_xmlfile` is a provisional function and may not exist in future versions.")

    # print out a psx project
    import xml.etree.ElementTree as ET
    if not fname:
        project_name = Path(cwd).stem
        fname = cwd
        cwd = Path(cwd).parent.as_posix()
    print("---",Path(fname).name)
    tree = ET.parse(fname)
    root = tree.getroot()
    parse_xml(cwd, root, project_name)


if __name__ == "__main__":
    pass
